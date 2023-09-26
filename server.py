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
user_id = 'U05TJES4796'

# create table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT)")

rows = cursor.execute("SELECT message, sender FROM my_slack_bot").fetchall()
rows.reverse()

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

                    # Fetch user information to get the user's display name
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
def get_latest_dms():
    latest_dms = []
    
    cursor.execute("SELECT DISTINCT sender FROM my_slack_bot")
    unique_senders = cursor.fetchall()
    
    for sender in unique_senders:
        cursor.execute("SELECT message FROM my_slack_bot WHERE sender = ? ORDER BY ROWID DESC LIMIT 1", sender)
        result = cursor.fetchone()
        if result:
            message_text = result[0]
            latest_dms.append(f"Latest DM from {sender[0]}: {message_text}")
    
    return latest_dms

# Function to send a message to the test channel
def schedule_message():
    current_time = datetime.datetime.now()
    
    if current_time.weekday() == 1 and current_time.hour == 13 and current_time.minute == 31:
        latest_dms = get_latest_dms()
        for dm in latest_dms:
            send_scheduled_message(dm)

# Function to send a message to the test channel
def send_scheduled_message(message_text):
    try:
        client.chat_postMessage(
            channel='#test', 
            text=message_text
        )
        print(f'Sent scheduled message to #test channel: {message_text}')
    except SlackApiError as e:
        print(f"Error sending scheduled message to #test channel: {e.response['error']}")

# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    schedule_message()
    time.sleep(10)  # interval in seconds (adjust as needed)
