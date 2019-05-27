import os
import time
from datetime import datetime
import json
import logging
from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO

from car import Car
from camera import Camera

from utils.KeepAliveTimer import KeepAliveTimer

app = Flask(__name__)
socketio = SocketIO(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

@app.route('/')
def main():
    return render_template('index.html')


@socketio.on("start_recording")
def start_record():
    print("Start recording...")
    car.is_recording = True


@socketio.on("stop_recording")
def stop_record():
    print("Stop recording...")
    car.is_recording = False

@socketio.on("healthcheck")
def healthcheck():
    """This event is emitted frequently by the frontend.
    It allows us to ensure there is someone controlling the car."""

    keep_alive_timer.run()

@socketio.on("gamepad_input")
def gamepad_input(angle_input, throttle_input):
    car.input = (angle_input, throttle_input)

@socketio.on("gamepad_out")
def gamepad_out():
    print("Gamepad out! Stopping...")
    car.is_recording = False

def on_healthcheck_too_long():
    print("Healcheck delay exceeded! Stopping...")
    car.is_recording = False

if __name__ == '__main__':
    camera = Camera()
    # Wait a bit to ensure that the camera started
    time.sleep(10)
    car = Car(camera)

    healthcheck_delay = 2
    keep_alive_timer = KeepAliveTimer(healthcheck_delay, on_healthcheck_too_long)

    socketio.run(app, host="0.0.0.0", port=5000)
