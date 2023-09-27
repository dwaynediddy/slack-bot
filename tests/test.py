from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    response_message = "hello"

    return response_message

if __name__ == '__main__':
    app.run(port=5000)
