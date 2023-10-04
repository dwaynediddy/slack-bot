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

# connect to sqlite
conn = sqlite3.connect('my_slack_bot.db')
cursor = conn.cursor()

conversation_id = 'D05SVH4BXDK'

# create table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT, status TEXT DEFAULT 'unsent')")

# Set to store unique user/message combinations
unique_messages = set()

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

                    # Fetch the last message sent by the user
                    cursor.execute("SELECT message FROM my_slack_bot WHERE sender = ? AND unique_key = '' ORDER BY ROWID DESC LIMIT 1", (sender_id,))
                    last_user_message = cursor.fetchone()

                    if last_user_message and last_user_message[0] == message_text:
                        # Current message is the same as the last message, stop storing messages from this sender
                        break
                    else:
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
    # Fetch the last message sent by the user to the bot
    cursor.execute("SELECT message FROM my_slack_bot WHERE sender = ? AND unique_key = '' ORDER BY ROWID DESC LIMIT 1", (sender_id,))
    last_user_message = cursor.fetchone()

    # Check if the user's message is the same as the last message they sent
    if last_user_message and last_user_message[0] == message:
        print(f"Message from {sender} is the same as the last message they sent, not storing.")
    else:
        cursor.execute("INSERT INTO my_slack_bot (message, sender) VALUES (?, ?)", (message, sender,))
        conn.commit()
        print(f"Stored DM: {message} from {sender}")



def send_latest_unsent_dms():
    cursor.execute("SELECT DISTINCT sender, message FROM my_slack_bot")
    unique_messages_in_db = cursor.fetchall()

    for sender, message_text in unique_messages_in_db:
        if (sender, message_text) not in unique_messages:
            sender_name = get_sender_name(sender)
            send_scheduled_message(message_text, sender_name, sender)

# Fetch sender's name based on user ID
def get_sender_name(sender_id):
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

    return sender_name

# Function to send a message to the test channel
def schedule_message():
    current_time = datetime.datetime.now() 

    # Set this line to when you want the bot to post using for testing over a period of time
    if (
        (current_time.weekday() == 2 and current_time.hour == 22 and current_time.minute == 24) or
        (current_time.weekday() == 2 and current_time.hour == 22 and current_time.minute == 25) or
        (current_time.weekday() == 2 and current_time.hour == 22 and current_time.minute == 26) or
        (current_time.weekday() == 2 and current_time.hour == 22 and current_time.minute == 27)     
    ):
        send_latest_unsent_dms()

# Function to send a message to the test channel
def send_scheduled_message(message_text, sender_name, sender_id):
    try:
        # Fetch the unique key of the last message sent by the bot to the test channel
        cursor.execute("SELECT unique_key FROM my_slack_bot WHERE sender = ? AND unique_key = 'sent' ORDER BY ROWID DESC LIMIT 1", ('bot',))
        last_bot_unique_key = cursor.fetchone()

        # Fetch the unique key of the current message
        cursor.execute("SELECT unique_key FROM my_slack_bot WHERE sender = ? AND message = ?", (sender_id, message_text))
        current_message_unique_key = cursor.fetchone()

        if last_bot_unique_key and current_message_unique_key and last_bot_unique_key[0] == current_message_unique_key[0]:
            print(f"Message from {sender_name} has the same unique key as the last message, not sending.")
        else:
            client.chat_postMessage(
                channel='#test', 
                text=f'{sender_name} says: {message_text}'
            )
            print(f'Sent scheduled message to #test channel: {message_text} from {sender_name}')
            
            # Mark the message as "sent" in the database
            new_timestamp = f'sent:{int(time.time())}'
            cursor.execute("UPDATE my_slack_bot SET unique_key = ? WHERE sender = ? AND message = ?", (new_timestamp, sender_id, message_text))
            conn.commit()
    except SlackApiError as e:
        print(f"Error sending scheduled message to #test channel: {e.response['error']}")
        
# When you send a message, update its status to 'sent'
def mark_message_as_sent(sender_id, message_text):
    cursor.execute("UPDATE my_slack_bot SET status = 'sent' WHERE sender = ? AND message = ?", (sender_id, message_text))
    conn.commit()

# Function to send unsent messages
def send_unsent_messages():
    cursor.execute("SELECT sender, message FROM my_slack_bot WHERE status = 'unsent' LIMIT 5")
    unsent_messages = cursor.fetchall()

    for sender, message_text in unsent_messages:
        sender_name = get_sender_name(sender)
        send_scheduled_message(message_text, sender_name, sender)
        mark_message_as_sent(sender, message_text)

# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    schedule_message()
    # Set an appropriate interval for checking messages (e.g., 1 minute)
    time.sleep(30)
