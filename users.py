import os
from slack_sdk import WebClient
from dotenv import load_dotenv 

load_dotenv()

# Initialize the WebClient with your bot's token
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

# Specify the user ID as the channel parameter
user_id = 'U05TJES4796'

# Message content
message_text = 'Hello, this is a private message to the user.'

# Send a private message to the user
client.chat_postMessage(
    channel=user_id,
    text=message_text
)



