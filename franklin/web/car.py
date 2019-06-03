import os
import time
from datetime import datetime
import json
from threading import Thread

import numpy as np
from PIL import Image
from tensorflow.python.keras.models import load_model

class Car():
    def __init__(self, camera, controller):
        self.input = (None, None)
        self.__is_recording = False
        self.__current_model = None
        self.active_model = None
        self.is_driving = True
        self.camera = camera
        self.controller = controller
        self.current_index = None

        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.images_dir = os.path.join(current_dir, "images")
        self.models_dir = os.path.join(current_dir, "models")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.file_pattern = "image_{index}_{angle}.jpg"

        self.angle_binned_size = 5

        # Thread that controls the car
        self.drive_thread = Thread(target=self.drive)
        self.drive_thread.start()

        # Thread that records images
        self.record_thread = Thread(target=self.record_images)
        self.record_thread.start()

    @property
    def is_recording(self):
        return self.__is_recording

    @is_recording.setter
    def is_recording(self, value):
        assert isinstance(value, bool)
        self.current_index = self.get_last_index()
        self.__is_recording = value

    @property
    def current_model(self):
        return self.__current_model

    @current_model.setter
    def current_model(self, value):
        if value is None:
            self.__current_model = None
            self.active_model = None
        else:
            self.is_driving = False
            self.__current_model = value

            model_path = os.path.join(self.models_dir, "5-essai.hdf5")
            self.active_model = load_model(model_path)
            self.is_driving = True

    def predict_angle(self, img_arr):
        img_arr = img_arr/255 - 0.5
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        angle_binned = self.active_model.predict(img_arr)
        result = angle_binned.argmax()*2/(5-1) - 1, 0
        return result

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
            start_time = time.time()

            file_name = self.file_pattern.format(
                index=self.current_index, angle=angle)
            
            self.save_image(self.camera.frame, file_name)

            sleep_time = (50/1000) - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def drive(self):
        while True:
            if not self.is_driving:
                continue

            start_time = time.time()

            # We're using a model
            if self.current_model is not None:
                # Use the prediction
                angle, _ = self.predict_angle(self.camera.frame)
                throttle = self.input[1]
            else:
                angle, throttle = self.input
                if angle is None or throttle is None:
                    continue

            self.controller.set_pulses((angle, throttle))

            sleep_time = (50/1000) - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)
            
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
