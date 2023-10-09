import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import sqlite3
import datetime
import time

load_dotenv()

slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_bot_token)

# Connect to SQLite database
conn = sqlite3.connect('my_slack_bot.db')
cursor = conn.cursor()

conversation_id = 'D05SVH4BXDK'

# Create table if it doesn't exist with is_sent column
# cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT, is_sent BOOLEAN DEFAULT 0, UNIQUE(sender, message))")
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message_id INTEGER PRIMARY KEY, message TEXT, sender TEXT, is_sent BOOLEAN)")


# Dictionary to track senders who have sent a duplicate message
senders_with_duplicate = {}

# Function to get and store new messages
def get_and_store_new_messages():
    try:
        response = client.conversations_history(
            channel=conversation_id,
        )

        if response['ok']:
            messages = response['messages']
            for message in reversed(messages):  # Start with the newest message
                if 'user' in message and 'text' in message:
                    sender_id = message['user']
                    message_text = message['text']

                    if sender_id in senders_with_duplicate:
                        # Sender has already sent a duplicate, skip this message
                        continue

                    # Fetch the last message sent by the user
                    cursor.execute("SELECT message FROM my_slack_bot WHERE sender = ? ORDER BY ROWID DESC LIMIT 1", (sender_id,))
                    last_user_message = cursor.fetchone()

                    if last_user_message and last_user_message[0] == message_text:
                        # Current message is the same as the last message they sent, stop storing messages from this sender
                        senders_with_duplicate[sender_id] = True  # Mark sender as having sent a duplicate
                        continue
                    else:
                        senders_with_duplicate.pop(sender_id, None)  # Reset sender status

                    # Fetch user information to get the user's display name (needs a display name set or will be blank)
                    try:
                        user_info_response = client.users_info(user=sender_id)
                        if user_info_response['ok']:
                            user_info = user_info_response['user']
                            if 'profile' in user_info and 'display_name' in user_info['profile']:
                                sender_name = user_info['profile']['display_name']
                            else:
                                sender_name = user_info['real_name_normalized'] if 'real_name_normalized' in user_info else sender_id
                                print('User display name not found, using real name')
                        else:
                            sender_name = sender_id
                            print('User info request failed')
                    except SlackApiError as e:
                        print(f"Error fetching user info: {e.response['error']}")
                        sender_name = sender_id

                    store_dm(message_text, sender_name, sender_id)

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")


# Function to store unique and newest messages
def store_dm(message, sender, sender_id):
    # Check if the message already exists for the sender
    cursor.execute("SELECT 1 FROM my_slack_bot WHERE sender = ? AND message = ? AND is_sent = 0", (sender_id, message))
    existing_message = cursor.fetchone()

    if not existing_message:
        # Message doesn't exist, insert it
        cursor.execute("INSERT INTO my_slack_bot (message, sender, is_sent) VALUES (?, ?, 0)", (message, sender))
        conn.commit()
        print(f"Stored DM: {message} from {sender}")
    else:
        print(f"Message already exists: {message} from {sender}")

# Function to send a message to the test channel
def send_scheduled_message(message_text, sender_id):
    try:
        # Check if the message has already been sent
        cursor.execute("SELECT is_sent FROM my_slack_bot WHERE sender = ? AND message = ?", (sender_id, message_text))
        sent_status = cursor.fetchone()

        if not sent_status or not sent_status[0]:
            print("Sending scheduled message...")
            user_info_response = client.users_info(user=sender_id)
            if user_info_response['ok']:
                user_info = user_info_response['user']
                if 'profile' in user_info and 'display_name' in user_info['profile']:
                    sender_name = user_info['profile']['display_name']
                else:
                    sender_name = user_info['real_name_normalized'] if 'real_name_normalized' in user_info else sender_id
                    print('User display name not found, using real name')
            else:
                sender_name = sender_id
                print('User info request failed')

            client.chat_postMessage(
                channel='#test', 
                text=f'{sender_name} says: {message_text}'
            )
            print(f'Sent scheduled message to #test channel: {message_text} from {sender_name}')

            # Mark the message as sent
            mark_message_as_sent(sender_id, message_text)
        else:
            print(f'Skipping message: {message_text}, already marked as sent.')

    except SlackApiError as e:
        print(f"Error sending scheduled message to #test channel: {e.response['error']}")

# Function to mark a message as sent
def mark_message_as_sent(sender_id, message_text):
    cursor.execute("UPDATE my_slack_bot SET is_sent = 1 WHERE sender = ? AND message = ?", (sender_id, message_text))
    conn.commit()

# Function to send the latest unsent messages
def send_latest_unsent_dms():
    cursor.execute("SELECT DISTINCT sender, message FROM my_slack_bot WHERE is_sent = 0")
    unsent_messages = cursor.fetchall()

    for sender, message_text in unsent_messages:
        sender_name = get_sender_name(sender)
        send_scheduled_message(message_text, sender_name, sender)


# Function to schedule sending messages at a specific day and time
def schedule_message():
    current_time = datetime.datetime.now() 
    desired_day = 0  # 0 being Monday, etc. 
    desired_hour = 12  # hour
    desired_minute = 17  # minute

    if (
        current_time.weekday() == desired_day and
        current_time.hour == desired_hour and
        current_time.minute == desired_minute
    ):
        send_latest_unsent_dms()  # Call the function to send unsent messages

# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    schedule_message()
    # Set an appropriate interval for checking messages (e.g., 1 minute)
    time.sleep(60)
