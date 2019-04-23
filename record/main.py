import os
import time
import json
import logging
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO

from car import Car

app = Flask(__name__)
socketio = SocketIO(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def main():
    return render_template('index.html')


@socketio.on("start_recording")
def start_record():
    print("Recording...")
    car.is_recording = True


@socketio.on("stop_recording")
def stop_record():
    print("Stopping recording...")
    car.is_recording = False


@socketio.on("check")
def health_check():
    print("Latest input: {}".format(car.input))

@socketio.on("gamepad_input")
def gamepad_input(angle_input, throttle_input):
    car.input = (angle_input, throttle_input)
    print("INPUT RECEIVED: {}".format(car.input))

@socketio.on("gamepad_out")
def gamepad_out():
    print("gamepad out")

if __name__ == '__main__':
    car = Car(1)
    socketio.run(app)
