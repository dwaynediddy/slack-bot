from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello"

@app.route('/slash')
def slash_command():
    return "Hello this is the slash route"

if __name__ == '__main__':
    app.run()