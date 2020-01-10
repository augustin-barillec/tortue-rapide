import os
import subprocess
import logging
from datetime import datetime

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
          outputs=['user/angle1', 'user/throttle1', 'user/mode', 'recording'],
          threaded=True)

    internet_checker = InternetChecker()

    V.add(internet_checker,
          outputs=['internet'],
          threaded=True)

    def stop_if_no_internet(internet, user_angle_1, user_throttle_1):
        if internet:
            return user_angle_1, user_throttle_1
        else:
            logger.warn('stopping')
            # cmd = "sudo wpa_supplicant -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf -B".split(" ")
            cmd = "sudo reboot".split(" ")
            subprocess.run(cmd)
            return 0, 0

    stop_if_no_internet_part = Lambda(stop_if_no_internet)

    V.add(stop_if_no_internet_part,
          inputs=['internet', 'user/angle1', 'user/throttle1'],
          outputs=['user/angle', 'user/throttle'])

    def pilot_condition(mode):
        if mode == 'user':
            return False
        else:
            return True

    pilot_condition_part = Lambda(pilot_condition)
    V.add(pilot_condition_part, inputs=['user/mode'],
          outputs=['run_pilot'])

    if model_path:
        model = load_model(model_path)
        model_wrapper_class = getattr(model_wrappers, model_wrapper)
        model_instance = model_wrapper_class(model=model)

        V.add(model_instance, inputs=['cam/image_array'],
              outputs=['pilot/angle1', 'pilot/throttle1'],
              run_condition='run_pilot')

        def bound_throttle(pilot_angle1, pilot_throttle1):
            if pilot_angle1 is None:
                pilot_angle1 = 0
            if pilot_throttle1 is None:
                pilot_throttle1 = 0
            pilot_throttle = min(1, pilot_throttle1)
            pilot_throttle = max(0, pilot_throttle)
            return pilot_angle1, pilot_throttle

        bound_throttle_part = Lambda(bound_throttle)

        V.add(bound_throttle_part,
              inputs=['pilot/angle1', 'pilot/throttle1'],
              outputs=['pilot/angle', 'pilot/throttle'])

    set_path = os.path.join(ROOT_PATH, "set_{}".format(
        datetime.now().strftime("%Y%m%d%H%M%S")))
    os.makedirs(set_path)
    inputs = ['cam/image_array', 'user/angle', 'user/throttle']  # 'user/mode'
    rec = Recorder(path=set_path)
    V.add(rec, inputs=inputs, run_condition='recording')

    def drive_mode(mode,
                   user_angle, user_throttle,
                   pilot_angle, pilot_throttle):
        if mode == 'user':
            return user_angle, user_throttle

        elif mode == 'local_angle':
            return pilot_angle, user_throttle

        else:
            return pilot_angle, pilot_throttle

    drive_mode_part = Lambda(drive_mode)
    V.add(drive_mode_part,
          inputs=['user/mode', 'user/angle', 'user/throttle',
                  'pilot/angle', 'pilot/throttle'],
          outputs=['angle', 'throttle'])
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
    if args.debug :
        logger.setLevel(logging.DEBUG)

    drive(cfg, model_path=args.model_path,
          model_wrapper=args.model_wrapper, debug=args.debug)
