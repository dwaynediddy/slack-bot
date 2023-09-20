import os
from slack_sdk import WebClient
from dotenv import load_dotenv 

load_dotenv()

# Initialize the WebClient with your bot's token
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

# Specify the user ID as the channel parameter
user_id = 'U05TJES4796' #diddy
# user_id='U05T6MR0CBW' #test acc

response = client.conversations_open(users=[user_id])

if response['ok']:
    conversation_id = response['channel']['id']
    message = 'This is a DM from a Bot'
    
    client.chat_postMessage(
        channel=conversation_id,
        text=message
    )
else:
    print('failed to DM')



