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
        user_info_response = client.users_info(user=new_member_id)  # Use new_member_id to fetch user info
        if user_info_response['ok']:
            user_info = user_info_response['user']
            if 'profile' in user_info and 'display_name' in user_info['profile']:
                sender_name = user_info['profile']['display_name']
            else:
                sender_name = user_info['real_name_normalized'] if 'real_name_normalized' in user_info else new_member_id
                print('User display name not found, using real name')
        else:
            sender_name = new_member_id
            print('User info request failed')
    except SlackApiError as e:
        print(f"Error fetching user info: {e.response['error']}")
        sender_name = new_member_id

    welcome_message = f"Welcome {sender_name} to the team! We're glad to have you here."

    try:
        # Send a DM to the new member
        dm_response = client.chat_postMessage(channel=new_member_id, text=f"Hello {sender_name}, welcome to the team!")
        print(f"Sent DM to {sender_name}: {dm_response['ts']}") 

        # Send a welcome message to the #test channel
        client.chat_postMessage(channel='#test', text=welcome_message)
        print(welcome_message)
    except SlackApiError as e:
        print(f"Error sending welcome message or DM: {e.response['error']}")

# send to new user
# using my own id for now
event_data = {
    "event": {
        "user": {
            "id": "U05TJES4796"
        }
    }
}
handle_team_join(event_data)
