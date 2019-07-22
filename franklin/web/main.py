import os
import time
from datetime import datetime
import json
import logging
from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO

from Car import Car
from Camera import Camera
from Controller import Controller

from utils.KeepAliveTimer import KeepAliveTimer
from tensorflow.python.keras.models import load_model

from unittest.mock import Mock

app = Flask(__name__)
socketio = SocketIO(app)

log = logging.getLogger('werkzeug')
# log.setLevel(logging.WARNING)

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

@socketio.on("set_model")
def set_model(name):
    car.stop_all()
    if name == "":
        print("Switching to human mode")
        car.current_model = None
    else:
        print("Switching to {} model".format(name))
        car.current_model = name
    car.start_all()

@socketio.on("start_pilot")
def start_pilot():
    print("Starting autopilot")
    current_dir = os.path.abspath(os.path.dirname(__file__))
    models_dir = os.path.join(current_dir, "models")
    car.model_path = os.path.join(models_dir, "5-essai.hdf5")

@socketio.on("stop_pilot")
def stop_pilot():
    print("Stopping autopilot")
    car.autopilot = False

def on_healthcheck_too_long():
    print("Healcheck delay exceeded! Stopping...")
    car.is_recording = False

if __name__ == '__main__':
    # current_dir = os.path.abspath(os.path.dirname(__file__))
    # models_dir = os.path.join(current_dir, "models")
    # model_path = os.path.join(models_dir, "5-essai.hdf5")
    # model = load_model(model_path)

    # Set up camera
    camera = Camera()
    # Wait a bit to ensure that the camera started
    time.sleep(10)

    # Set up car controller
    controller = Controller()

    # Set up recording
    car = Car(camera, controller)

    # Set up health check timer
    healthcheck_delay = 2
    keep_alive_timer = KeepAliveTimer(healthcheck_delay, on_healthcheck_too_long)

    socketio.run(app, host="0.0.0.0", port=5000)
