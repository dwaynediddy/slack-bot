from flask import Flask, request, jsonify
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import sqlite3
import datetime
import time

load_dotenv()

slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

# connect to sqlite
conn = sqlite3.connect('my_slack_bot.db')
cursor = conn.cursor()

conversation_id = 'D05SVH4BXDK'

# create table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS my_slack_bot (message TEXT, sender TEXT, unique_key TEXT)")

rows = cursor.execute("SELECT message, sender FROM my_slack_bot").fetchall()


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/store_dm', methods=['POST'])
def store_dm_endpoint():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message')
        sender = data.get('sender')
        
        if message and sender:
            store_dm(message, sender)
            return jsonify({'message': "Dm stored successfully"}), 200
        else:
            return jsonify({'message': 'Invalid request'}), 400
        
@app.route('/send_scheduled_message', methods=['POST'])
def send_scheduled_message_endpoint():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message')
        sender_name = data.get('sender_name')

        if message and sender_name:
            send_scheduled_message(message, sender_name)
            return jsonify({"message": "Scheduled message sent successfully"}), 200
        else:
            return jsonify({"message": "Invalid request data"}), 400

if __name__ == '__main__':
    app.run()