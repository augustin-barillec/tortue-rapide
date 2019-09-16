
from PIL import Image

import os
import numpy as np
from datetime import datetime


class Recorder(object):

    def __init__(self, path):
        self.path = path
        self.id = 0

    # inputs = ['cam/image_array', 'user/angle', 'user/throttle', 'timestamp']
    def run(self, im_arr, angle, throttle):

        # record image
        img = Image.fromarray(np.uint8(im_arr))
        name = self.make_file_name(angle, throttle, ext='.jpg')
        img.save(os.path.join(self.path, name))

    def make_file_name(self, angle, throttle, ext='.jpg'):
        angle = round(angle, 2)
        throttle = round(throttle, 2)
        return "{}_{}_{}{}".format(datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3], angle, throttle, ext)
        # return "{}_{}_{}{}".format(self.id, angle, throttle, ext)
