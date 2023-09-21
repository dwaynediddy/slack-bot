import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Initialize the WebClient with your bot's token
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

conversation_id = 'D05SVH4BXDK'  # conversation ID can be DM or channel

try:
    # Use the conversations.history method to retrieve messages
    response = client.conversations_history(
        channel=conversation_id,
        limit=100,  # more than 200 is not recoomended
    )

    if response['ok']:
        messages = response['messages']
        for message in reversed(messages):
            user_id = message['user']
            message_text = message['text']

            # Process and use the user's reply as needed
            print(f"User ID: {user_id}")
            print(f"Message Text: {message_text}")
    else:
        print('Failed to retrieve messages. Error:', response['error'])

except SlackApiError as e:
    print(f"Error: {e.response['error']}")
    
