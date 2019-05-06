import os
import time
import json
import logging
import cv2
from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO

from car import Car
from utils.KeepAliveTimer import KeepAliveTimer

app = Flask(__name__)
socketio = SocketIO(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
    print("INPUT RECEIVED: {}".format(car.input))

@socketio.on("gamepad_out")
def gamepad_out():
    print("Gamepad out! Stopping...")
    car.is_recording = False

# def send_latest_image():
#     while True:
#         socketio.emit("latest_image", car.latest_image)
#         print("sending_image")
#         time.sleep(1)

def on_healthcheck_too_long():
    print("Healcheck delay exceeded! Stopping...")
    car.is_recording = False

if __name__ == '__main__':
    car = Car(1)
    healthcheck_delay = 2
    keep_alive_timer = KeepAliveTimer(healthcheck_delay, on_healthcheck_too_long)
    # send_latest_thread = Thread(target=send_latest_image)
    # send_latest_thread.start()
    socketio.run(app)
