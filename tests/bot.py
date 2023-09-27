import os
from slack_sdk import WebClient
from dotenv import load_dotenv 

load_dotenv()

# Access the 'SLACK_BOT_TOKEN' environment variable
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

client.chat_postMessage(channel='#test', text='hello world!')
