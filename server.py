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
# user_id = 'U05T6MR0CBW'  # test acc

test_channel_id = 'C05SVHU936Z' #test channel id


# create table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT)")

cursor.execute("INSERT INTO my_slack_bot VALUES ('hello world', 'diddy')")
cursor.execute("INSERT INTO my_slack_bot VALUES ('just to wet the whistle?', 'Super Hans')")

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
    
# Function to send a message to the test channel
def send_scheduled_messaage(message_text):
    try:
        client.chat_postMessage(
            channel='#test',  # Replace with your test channel name or ID
            text=message_text
        )
        print(f'Sent message: {message_text} to #test channel')
    except SlackApiError as e:
        print(f"Error sending message to #test channel: {e.response['error']}")

# Schedule a message to be sent to the test channel at a specific datetime
def schedule_message():
    scheduled_time = datetime.datetime(2023, 9, 26, 12, 8)  # Adjust the datetime as needed
    current_time = datetime.datetime.now()
    
    if current_time >= scheduled_time:
        message_text = "This is a scheduled message to #test channel"
        send_scheduled_messaage(message_text)

# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    schedule_message()
    time.sleep(6000)  # interval in seconds
