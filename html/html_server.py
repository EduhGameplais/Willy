from typing import Literal
from flask import Flask, render_template

app = Flask(__name__)

current_emotion = "square"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/emotion")
def get_robot_emotion():
    return current_emotion

def set_emotion(emotion: Literal['square', 'happiness', 'sadness', 'angry', 'thinking', 'listening']):
    global current_emotion
    current_emotion = emotion
    
def start():
    app.run(host="0.0.0.0", port=8080, ssl_context=("html/cert.pem", "html/key.pem"))
    
start()