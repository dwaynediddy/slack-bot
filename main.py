import os
from flask import Flask
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, endpoint="/slack/events")

slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_bot_token)

@app.route('/slack/events', methods=['GET'])
def slack_event_callback():
    return 'hello world'

if __name__ == '__main__':
    app.run(debug=True)
