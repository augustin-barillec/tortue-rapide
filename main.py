import os
import subprocess
import logging
from datetime import datetime
import time

import tortue_rapide as dk
from tortue_rapide.parts.recorder import Recorder
from tortue_rapide.parts.transform import Lambda
from tortue_rapide.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from tortue_rapide.parts.controller import LocalWebController
from tensorflow.python.keras.models import load_model

from tortue_rapide.parts import model_wrappers
from tortue_rapide.parts.internet_checker import InternetChecker

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))


def drive(cfg, model_path=None, model_wrapper=None, debug=False):

    V = dk.vehicle.Vehicle()

    if not debug:
        from tortue_rapide.parts.camera import PiCamera
        cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
        V.add(cam, outputs=['cam/image_array'], threaded=True)

    else:
        logger.info("Debug : ignoring camera.")

        def fake_cam():
            from PIL import Image
            import numpy as np
            dir_path = os.path.dirname(os.path.realpath(__file__))
            img = Image.open(os.path.join(dir_path, 'img.jpg'))
            a = np.array(img)
            return a

        fake_cam_part = Lambda(fake_cam)
        V.add(fake_cam_part, outputs=['cam/image_array'])

    ctr = LocalWebController(use_chaos=False)

    V.add(ctr,
          inputs=['cam/image_array'],
          outputs=['user_angle', 'user_throttle'],
          threaded=True)

    internet_checker = InternetChecker()

    V.add(internet_checker,
          outputs=['internet'],
          threaded=True)

    def stop_if_no_internet(internet, user_angle, user_throttle):
        if internet:
            return user_angle, user_throttle
        else:
            logger.warn('stopping')
            return 0, 0

    def reconnect_if_no_internet(internet):
        if not internet:
            logger.info("Trying to reconnect...")
            # cmd = ["sudo killall wpa_supplicant", "&&",
            #         "sudo modprobe -rv rt2800usb", "&&"
            #         "sudo modprobe -v rt2800usb", "&&",
            #         "sudo wpa_supplicant -i wlan1 -c/etc/wpa_supplicant.conf -B", "&&",
            #         "sudo dhclient wlan1"]
            cmd = ["sudo reboot"]
            subprocess.run(cmd)

    stop_if_no_internet_part = Lambda(stop_if_no_internet)

    V.add(stop_if_no_internet_part,
          inputs=['internet', 'user_angle', 'user_throttle'],
          outputs=['angle', 'throttle'])

    reconnect_if_no_internet_part = Lambda(reconnect_if_no_internet)

    V.add(reconnect_if_no_internet_part,
          inputs=['internet'])

    if not debug:
        steering_controller = PCA9685(cfg.STEERING_CHANNEL)
        steering = PWMSteering(controller=steering_controller,
                               left_pulse=cfg.STEERING_LEFT_PWM,
                               right_pulse=cfg.STEERING_RIGHT_PWM)

        throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL)
        throttle = PWMThrottle(controller=throttle_controller,
                               max_pulse=cfg.THROTTLE_FORWARD_PWM,
                               zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                               min_pulse=cfg.THROTTLE_REVERSE_PWM)

        V.add(steering, inputs=['angle'])
        V.add(throttle, inputs=['throttle'])

    else:
        logger.debug("Debug : ignoring controller part.")

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)


if __name__ == '__main__':
    cfg = dk.load_config()

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', '-m', required=False, type=str)
    parser.add_argument('--model_wrapper', '-w', required=False, type=str)
    parser.add_argument('--debug', '-d', required=False, action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(module)-10s :: %(message)s")
    logger = logging.getLogger(__name__)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    drive(cfg, model_path=args.model_path,
          model_wrapper=args.model_wrapper, debug=args.debug)
