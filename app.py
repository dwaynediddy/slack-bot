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
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT, is_sent BOOLEAN)")


# Function to get and store new messages
def get_and_store_new_messages():
    try:
        response = client.conversations_history(
            channel=conversation_id,
            # checking last 10 messages (can be more)
            limit=10
        )

        if response['ok']:
            messages = response['messages']
            for message in reversed(messages):  # Reverse the order when storing
                if 'user' in message and 'text' in message:
                    sender_id = message['user']
                    message_text = message['text']

                    # Fetch user information to get the user's display name (needs a display name set or will be blank)
                    try:
                        user_info_response = client.users_info(user=sender_id)
                        if user_info_response['ok']:
                            user_info = user_info_response['user']
                            if 'profile' in user_info and 'display_name' in user_info['profile']:
                                sender_name = user_info['profile']['display_name']
                            else:
                                sender_name = user_info[
                                    'real_name_normalized'] if 'real_name_normalized' in user_info else sender_id
                                print('User display name not found, using real name')
                        else:
                            sender_name = sender_id
                            print('User info request failed')
                    except SlackApiError as e:
                        print(f"Error fetching user info: {e.response['error']}")
                        sender_name = sender_id

                    store_dm(message_text, sender_name)

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")


def store_dm(message, sender):
    # Check if the message already exists
    cursor.execute("SELECT 1 FROM my_slack_bot WHERE sender = ? AND message = ?", (sender, message))
    existing_message = cursor.fetchone()

    if not existing_message:
        # Check if the message was already sent
        cursor.execute("SELECT is_sent FROM my_slack_bot WHERE sender = ? AND message = ?", (sender, message))
        sent_status = cursor.fetchone()

        if not sent_status or not sent_status[0]:
            cursor.execute("INSERT INTO my_slack_bot (message, sender, is_sent) VALUES (?, ?, 0)", (message, sender,))
            conn.commit()
            print(f"Stored DM: {message} from {sender}")
        else:
            print(f"Message from {sender} has already been sent, not storing again.")
    else:
        print(f"Message from {sender} has already been stored, not storing again.")


# Function to send all unsent messages in order of storage
def send_latest_unsent_dms():
    cursor.execute("SELECT DISTINCT sender FROM my_slack_bot WHERE is_sent = 0")
    senders = cursor.fetchall()

    for sender_row in senders:
        sender = sender_row[0]
        cursor.execute("SELECT message FROM my_slack_bot WHERE sender = ? AND is_sent = 0 ORDER BY rowid ASC",
                       (sender,))
        unsent_messages = cursor.fetchall()

        for message_row in unsent_messages:
            message_text = message_row[0]
            send_scheduled_message(message_text, sender)


# Function to send a message to the test channel
def schedule_message():
    current_time = datetime.datetime.now()
    # current_time.weekday() == 1 and current_time.hour == 12 and current_time.minute == 38
    # send_latest_unsent_dms()

    # can replace the line above if you want multiple scheduled times
    if (
            (current_time.weekday() == 3 and current_time.hour == 11 and current_time.minute == 23) or
            (current_time.weekday() == 3 and current_time.hour == 11 and current_time.minute == 24) or
            (current_time.weekday() == 3 and current_time.hour == 11 and current_time.minute == 25)
    ):
        send_latest_unsent_dms()


# Function to send a message to the test channel
def send_scheduled_message(message_text, sender_name):
    try:
        client.chat_postMessage(
            channel='#test',
            text=f'{sender_name} says: {message_text}'
        )
        print(f'Sent scheduled message to #test channel: {message_text} from {sender_name}')

        # Mark the message as sent in the database
        cursor.execute("UPDATE my_slack_bot SET is_sent = 1 WHERE sender = ? AND message = ?",
                       (sender_name, message_text))
        conn.commit()

    except SlackApiError as e:
        print(f"Error sending scheduled message to #test channel: {e.response['error']}")


# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    schedule_message()
    # 21600 every 6 hours
    time.sleep(45)  # interval in seconds (adjust as needed)
