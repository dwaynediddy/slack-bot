import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import sqlite3
import datetime
import time

load_dotenv()

slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

# connect to sqlite
conn = sqlite3.connect('my_slack_bot.db')
cursor = conn.cursor()

conversation_id = 'D05SVH4BXDK'

# create table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT, unique_key TEXT)")

rows = cursor.execute("SELECT message, sender FROM my_slack_bot").fetchall()

# Function to get and store new messages
def get_and_store_new_messages():
    try:
        response = client.conversations_history(
            channel=conversation_id,
            limit=1
        )

        if response['ok']:
            messages = response['messages']
            for message in messages:
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
                                sender_name = user_info['real_name_normalized'] if 'real_name_normalized' in user_info else sender_id
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
    cursor.execute("INSERT INTO my_slack_bot (message, sender) VALUES (?, ?)", (message, sender))
    conn.commit()
    print(f"Stored DM: {message} from {sender}")

# Function to retrieve the latest DM from each user in the database
def send_latest_unsent_dms():
    cursor.execute("SELECT DISTINCT sender FROM my_slack_bot")
    unique_senders = cursor.fetchall()
    
    for sender in unique_senders:
        # Retrieve the LATEST message from users
        cursor.execute("SELECT message, sender, unique_key FROM my_slack_bot WHERE sender = ? ORDER BY ROWID DESC LIMIT 1", (sender[0],))
        result = cursor.fetchone()
        if result:
            message_text, sender_name, timestamp = result
            if not timestamp or not timestamp.startswith('sent:'):
                send_scheduled_message(message_text, sender_name)  # Include sender's name
                # Mark the message as "sent" in the database
                new_timestamp = f'sent:{int(time.time())}'
                cursor.execute("UPDATE my_slack_bot SET unique_key = ? WHERE sender = ? AND unique_key = ?", (new_timestamp, sender[0], timestamp))
                conn.commit()

# Function to send a message to the test channel
def schedule_message():
    current_time = datetime.datetime.now()
    
    if current_time.weekday() == 0 and current_time.hour == 9 and current_time.minute == 30:
            send_latest_unsent_dms()

# Function to send a message to the test channel
def send_scheduled_message(message_text, sender_name):
    try:
        client.chat_postMessage(
            channel='#test', 
            text=f'{sender_name} says: {message_text}'
        )
        print(f'Sent scheduled message to #test channel: {message_text} from {sender_name}')
    except SlackApiError as e:
        print(f"Error sending scheduled message to #test channel: {e.response['error']}")

# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    schedule_message()
    # 21600 every 6 hours
    time.sleep(21600)  # interval in seconds (adjust as needed)
