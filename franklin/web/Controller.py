import time
from unittest.mock import Mock

import Adafruit_PCA9685
from utils import data_utils

MAX_THROTTLE = 390
MIN_THROTTLE = 330
ZERO_THROTTLE = 360

MAX_LEFT = 480
MAX_RIGHT = 310

class Controller:
    def __init__(self, throttle_channel=0, steer_channel=1):
        self.steer_channel = steer_channel
        self.throttle_channel = throttle_channel

        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm = Mock()
        self.pwm.set_pwm_freq(60)

    def set_pulses(self, input_):
        angle, throttle = input_

        try:
            self.set_steer(angle)
            self.set_throttle(throttle)
        except OSError as e:
            print("PMW setting failed!\n{}".format(e))

    def set_steer(self, angle):
        pulse = data_utils.data.map_range(
            angle,
            -1, 1,
            MAX_LEFT, MAX_RIGHT
        )

        self.pwm.set_pwm(self.steer_channel, 0, pulse)

    def set_throttle(self, throttle):
        if throttle > 0:
            pulse = data_utils.map_range(throttle,
                                         0, 1,
                                         ZERO_THROTTLE, MAX_THROTTLE)
        else:
            pulse = data_utils.map_range(throttle,
                                         -1, 0,
                                         MIN_THROTTLE, ZERO_THROTTLE)

        self.pwm.set_pwm(self.steer_channel, 0, pulse)

    def stop(self):
        self.set_steer(0)
        self.set_throttle(0)
