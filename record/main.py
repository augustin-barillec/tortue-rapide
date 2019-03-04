import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def main():
    return render_template('index.html')

@socketio.on("start_recording")
def start_record():
    print("Recording...")
    # Get the 

@socketio.on("stop_recording")
def stop_record():
    print("Stopping recording...")

if __name__ == '__main__':
    socketio.run(app)
