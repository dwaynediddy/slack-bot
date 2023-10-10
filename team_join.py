import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


load_dotenv()

# Initialize your Slack client with your bot token
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_bot_token)

# Event handler for the team_join event
def handle_team_join(event_data):
    new_member_id = event_data['event']['user']['id']  # Access the user ID from the event data
    welcome_message = f"Welcome <@{new_member_id}> to the team! We're glad to have you here."
    try:
        client.chat_postMessage(channel='#test', text=welcome_message)
        print(welcome_message)
    except SlackApiError as e:
        print(f"Error sending welcome message: {e.response['error']}")


# This function shouold be called when somoeoen new joions
# Use own id oor somoeone in channel to siimulate joioning
event_data = {
    "event": {
        "user": {
            "id": "UD05SNRH38JJ"
        }
    }
}
handle_team_join(event_data)


