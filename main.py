import os
from flask import Flask
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv('SLACK_SIGNING_SECRET'), "/slack/events")

slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_bot_token)

@app.route('/slack/events', methods=['POST'])
def slack_event_callback():
    if slack_events_adapter.server.verify_signature(request):
        return 'Verified'
    else:
        return 'Verification failed', 403

@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    # Handle app mentions
    pass

if __name__ == '__main__':
    app.run(debug=True)
