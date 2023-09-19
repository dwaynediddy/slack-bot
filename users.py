import os
from slack_sdk import WebClient

# Initialize the WebClient with your bot's token
slack_bot_token = 'SLACK_BOT_TOKEN'
client = WebClient(token=slack_bot_token)

# Specify the user ID as the channel parameter
user_id = 'U05TJES4796'

# Message content
message_text = 'Hello, this is a private message to the user.'

# Send a private message to the user
response = client.chat_postMessage(
    channel='#test',
    text=message_text
)

# Check if the message was sent successfully
# if response["ok"]:
#     print(f"Private message sent to user with user ID {user_id}")
# else:
#     print(f"Failed to send private message: {response['error']}")



