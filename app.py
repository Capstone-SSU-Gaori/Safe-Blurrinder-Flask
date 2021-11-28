from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route("/tospring")
def spring():
    return "test"

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)