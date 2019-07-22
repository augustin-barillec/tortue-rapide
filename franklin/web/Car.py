import os
import time
from datetime import datetime
import json
from threading import Thread

import numpy as np
from PIL import Image
from tensorflow import get_default_graph
from tensorflow.python import keras

BASE_RATE = 50 # The base rate for all threads, in milliseconds (1 drive decision, 1 record)

graph = get_default_graph()

class Car():
    def __init__(self, camera, controller):
        self.input = (None, None)
        self.__is_recording = False
        self.is_driving = True
        self.camera = camera
        self.controller = controller
        self.current_index = None
        self.run_record = True

        self.__model_path = None
        self.__model = None
        self.__load_model = False

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
        if value:
            # Safely get the latest image index from disk
            self.current_index = self.get_last_index()
            # The record thread might have been stopped (using a model), recreate it
            if self.record_thread is None:
                self.record_thread = Thread(target=self.record_images)
                self.record_thread.start()
        
        self.__is_recording = value

    @property
    def model_path(self):
        return self.__model_path

    @model_path.setter
    def model_path(self, value):
        # "Unsetting" the model
        # set the model to None to go back to manual driving mode
        if value is None:
            self.__model_path = None
            self.__model = None
        # Setting a model, only when a different model is selected
        elif self.__model_path != value:
            self.__model_path = value
            self.__load_model = True # The next loop of drive will load the new model
        
            
    def start_all(self):
        """Starts all the threads of all the different car parts."""
        
        print("Starting car parts...")
        self.run = True
        self.camera.run = True

        self.drive_thread = Thread(target=self.drive)
        self.record_thread = Thread(target=self.record_images)
        self.camera.thread = Thread(target=self.camera.consume)
        
        self.drive_thread.start()
        self.record_thread.start()
        self.camera.thread.start()

    def stop_all(self):
        """Stops the threads of all the different car parts."""

        print("Stopping car parts...")
        self.run = False
        self.camera.run = False

        self.drive_thread.join()
        self.record_thread.join()
        self.camera.thread.join()

    def load_model(self):

        # Stop the car for safety
        self.controller.stop()
        
        # Stop the other threads for faster load
        self.run_record = False
        self.camera.run = False
        self.record_thread.join()
        self.camera.thread.join()

        print("Loading model...")
        model = keras.models.load_model(self.__model_path)
        global graph
        graph = get_default_graph()
        print("Model loaded...")

        self.__model = model

        # Restart the camera thread
        self.camera.thread = Thread(target=self.camera.consume)
        self.camera.thread.start()

    def predict_angle(self, img_arr):
        img_arr = np.uint8(img_arr)
        img_arr = img_arr/255 - 0.5
        img_arr = img_arr.reshape((1,) + img_arr.shape)

        with graph.as_default():
            angle_binned = self.__model.predict(img_arr)
            result = angle_binned.argmax()*2/(5-1) - 1, 0
        return result

    def record_images(self):
        while self.run_record:
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

            self.sleep_to_rate(start_time, BASE_RATE)

    def drive(self):
        while True:
            if not self.is_driving:
                continue

            start_time = time.time()

            if self.__load_model:
                print("loading model")
                self.load_model()
                self.__load_model = False

            # We're using a model
            if self.__model is not None:
                # Use the prediction for the angle
                angle, _ = self.predict_angle(self.camera.frame)
                throttle = self.input[1]
            # We're not using a model
            else:
                # Use the inputs
                angle, throttle = self.input
                if angle is None or throttle is None:
                    self.controller.stop()
                    continue

            self.controller.set_pulses((angle, throttle))

            self.sleep_to_rate(start_time, BASE_RATE)
    
    def sleep_to_rate(self, start_time, rate_milliseconds):
        """Sleeps to respect the specified rate, if needed."""
        sleep_time = (rate_milliseconds/1000) - (time.time() - start_time)
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
