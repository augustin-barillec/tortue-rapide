#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car and train a model for it.

Usage:
    manage.py (drive) [--model=<model>] [--js] [--chaos]
    manage.py (train) [--tub=<tub1,tub2,..tubn>]  (--model=<model>) [--base_model=<base_model>] [--no_cache]

Options:
    -h --help        Show this screen.
    --tub TUBPATHS   List of paths to tubs. Comma separated. Use quotes to use wildcards. ie "~/tubs/*"
    --js             Use physical joystick.
    --chaos          Add periodic random steering when manually driving
"""
import os
from datetime import datetime

import donkeycar as dk
from donkeycar.parts.recorder import Recorder
from donkeycar.parts.transform import Lambda
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.controller import LocalWebController
from tensorflow.python.keras.models import load_model

from donkeycar.parts import model_wrappers

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))


def drive(cfg, model_path=None, model_wrapper=None, debug=False):
    """
    Construct a working robotic vehicle from many parts.
    Each part runs as a job in the Vehicle loop, calling either
    it's run or run_threaded method depending on the constructor flag `threaded`.
    All parts are updated one after another at the framerate given in
    cfg.DRIVE_LOOP_HZ assuming each part finishes processing in a timely manner.
    Parts may have named outputs and inputs. The framework handles passing named outputs
    to parts requesting the same named input.
    """

    V = dk.vehicle.Vehicle()

    if not debug:
        from donkeycar.parts.camera import PiCamera
        cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
        V.add(cam, outputs=['cam/image_array'], threaded=True)

    else:
        print("Debug : ignoring camera.")
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
          outputs=['user/angle', 'user/throttle', 'user/mode', 'recording'],
          threaded=True)

    # See if we should even run the pilot module.
    # This is only needed because the part run_condition only accepts boolean
    def pilot_condition(mode):
        if mode == 'user':
            return False
        else:
            return True

    pilot_condition_part = Lambda(pilot_condition)
    V.add(pilot_condition_part, inputs=['user/mode'],
                                outputs=['run_pilot'])

    # Run the pilot if the mode is not user.
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


    # add tub to save data

    set_path = os.path.join(ROOT_PATH, "set_{}".format(datetime.now().strftime("%Y%m%d%H%M%S")))
    os.makedirs(set_path)
    inputs = ['cam/image_array', 'user/angle', 'user/throttle']  # 'user/mode'
    rec = Recorder(path=set_path)
    V.add(rec, inputs=inputs, run_condition='recording')

    # Choose what inputs should change the car.
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
        print("Debug : ignoring controller part.")

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

    drive(cfg, model_path=args.model_path, model_wrapper=args.model_wrapper, debug=args.debug)
