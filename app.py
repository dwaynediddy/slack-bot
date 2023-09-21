from flask import Flask, request, jsonify
# import os
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
# from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)

@app.route('/slash-command', methods=['POST'])
def slash_command():
    data = request.form
    command = data.get('command')
    text = data.get('text')
    
    response_text = f'You entered: {text}'
    
    return jsonify({'text': response_text})

if __name__ == '__main__':
    app.run(debug=True)