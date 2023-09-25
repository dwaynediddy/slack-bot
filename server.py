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
user_id = 'U05TJES4796' #diddy


# create table if it doesnt exist
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
                    sender = message['user']
                    message_text = message['text']
                    store_dm(message_text, sender)

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")

def store_dm(message, sender):
    cursor.execute("INSERT INTO my_slack_bot (message, sender) VALUES (?, ?)", (message, sender))
    conn.commit()
    print(f"Stored DM: {message} from {sender}")

# Periodically check for new messages and store them
while True:
    get_and_store_new_messages()
    time.sleep(10)  # interval in seconds
