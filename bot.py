import os
from slack_sdk import WebClient
from pathlib import Path
from dotenv import load_dotenv 

load_dotenv()

# Access the 'SLACK_BOT_TOKEN' environment variable
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
#absolute joke that this has issues and dotenv has issues 
env_path = Path('.') / '.env'

slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

# client = WebClient(token='xoxb-5926145488753-5916507028626-2VFvmUEeymx1jx3tSMaB0s2r')


client.chat_postMessage(channel='#test', text='hello world!')