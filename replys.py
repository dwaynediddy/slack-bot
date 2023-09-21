import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Initialize the WebClient with your bot's token
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

conversation_id = 'D05SVH4BXDK'  # conversation ID can be DM or channel

def get_DM():
    try:
        # Use the conversations.history method to retrieve messages
        response = client.conversations_history(
            channel=conversation_id,
            limit=1 # get one message
        )
        
        if response['ok']:
            messages = response['messages']
            if messages:
                latest_dm = messages[0]['text']
                return latest_dm
            else:
                return None
        
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        return None

# Function to post a DM to another channel
def post_dm_test(message_text):
    try:
        response = client.chat_postMessage(
            channel='#test',
            text=message_text
        )
        
        if response['ok']:
            print('Message posted successfully.')
        else:
            print('Failed to post message. Error:', response['error'])
                
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")

latest_dm = get_DM()

if latest_dm is not None:
    post_dm_test(latest_dm)
else:
    print('No DM found from the user.')
