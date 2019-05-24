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
from docopt import docopt

import donkeycar as dk

from donkeycar.parts.camera import PiCamera
from donkeycar.parts.transform import Lambda
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubWriter
from donkeycar.parts.controller import LocalWebController
from donkeycar.parts.clock import Timestamp

from tensorflow.python.keras.models import load_model


def drive(cfg, model_path=None):
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

    clock = Timestamp()
    V.add(clock, outputs='timestamp')

    cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(cam, outputs=['cam/image_array'], threaded=True)

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
        model_basename = os.path.basename(model_path)



        angle_binned_size = int(model_basename.split('-')[0])

        def predict_angle(img_arr):
            img_arr = img_arr/255 - 0.5
            img_arr = img_arr.reshape((1,) + img_arr.shape)
            angle_binned = model.predict(img_arr)
            result = angle_binned.argmax()*2/(angle_binned_size-1) - 1, 0
            return result

        predict_angle_part = Lambda(predict_angle)
        V.add(predict_angle_part, inputs=['cam/image_array'],
                                  outputs=['pilot/angle', 'pilot/throttle'],
                                  run_condition='run_pilot')
    else:
        # add tub to save data
        inputs = ['cam/image_array', 'user/angle', 'user/throttle', 'user/mode', 'timestamp']
        types = ['image_array', 'float', 'float', 'str', 'str']
        tub = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
        V.add(tub, inputs=inputs, run_condition='recording')

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

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    if args['drive']:
        drive(cfg, model_path=args['--model'])






