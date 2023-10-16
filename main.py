import slack_sdk as slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Set up the Slack bot
slack_event_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

# Define the custom greeting message
GREETING_MESSAGE = "Hello {user_name}, welcome to the {channel_name} " \
                   "channel! We're excited to have you here."
# Keep track of the users that have already been welcomed
welcomed_users = set()


# Set up event listener for "member joined channel" event
@slack_event_adapter.on('member_joined_channel')
def handle_member_joined_channel(event_data):
    print(event_data)
    user_id = event_data['event']['user']
    channel_id = event_data['event']['channel']

    if user_id not in welcomed_users:
        welcomed_users.add(user_id)

        user_info = client.users_info(user=user_id)
        user_name = user_info['user']['name']

        channel_info = client.conversations_info(channel=channel_id)
        channel_name = channel_info['channel']['name']

        greeting = GREETING_MESSAGE.format(user_name=user_name, channel_name=channel_name)

        client.chat_postMessage(channel=channel_id, text=greeting)


if __name__ == "__main__":
    app.run(debug=True, port=4040)
