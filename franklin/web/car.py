import os
import time
import json
from threading import Thread

import numpy as np
from PIL import Image

class Car():
    def __init__(self, camera):
        self.input = (None, None)
        self.__is_recording = False

        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.images_dir = os.path.join(current_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        self.file_pattern = "image_{index}_{angle}_{throttle}.jpg"

        self.camera = camera
        self.current_index = None

        self.thread = Thread(target=self.record_images)
        self.thread.start()

    @property
    def is_recording(self):
        return self.__is_recording

    @is_recording.setter
    def is_recording(self, value):
        assert isinstance(value, bool)
        self.current_index = self.get_last_index()
        self.__is_recording = value

    def record_images(self):

        while True:
            if self.current_index is None:
                continue
            if not self.is_recording:
                continue
            
            angle, throttle = self.input
            if angle is None or throttle is None:
                continue

            self.current_index += 1
            # start_time = time.time()

            # data = {'ts': start_time}

            angle, throttle = self.input
            file_name = self.file_pattern.format(
                angle=angle, throttle=throttle, index=self.current_index)
            
            self.save_image(self.camera.frame, file_name)

            self.input = (None, None)

    def save_image(self, image_array, name):
        img = Image.fromarray(np.uint8(image_array))
        img.save(os.path.join(self.images_dir, name))

    def get_last_index(self):
        files = next(os.walk(self.images_dir))[2]
        image_files = [f for f in files if f[:5] == 'image']

        if len(image_files) < 1:
            return 0
        
        def get_file_idx(file_name):
            name = file_name.split('.')[0]
            return int(name.split('_')[1])

        return max([get_file_idx(f) for f in image_files])
