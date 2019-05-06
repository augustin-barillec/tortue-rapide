import os
import time
import json
from threading import Thread

class Car():
    def __init__(self, seconds):
        self.input = (None, None)
        self.seconds = seconds
        self.__is_recording = False
        self.latest_image = None

        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.images_dir = os.path.join(current_dir, "images")
        
        self.thread = Thread(target=self.record_images)
        self.thread.start()

    @property
    def is_recording(self):
        return self.__is_recording

    @is_recording.setter
    def is_recording(self, value):
        assert isinstance(value, bool)
        self.__is_recording = value

    def record_images(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        images_dir = os.path.join(current_dir, "images")
        file_pattern = "image_{index}_{angle}_{throttle}"

        i = self.get_last_index()

        while True:
            if not self.is_recording:
                continue
            
            angle, throttle = self.input
            if angle is None or throttle is None:
                continue

            i += 1
            start_time = time.time()

            data = {'ts': start_time}

            angle, throttle = self.input
            file_name = file_pattern.format(
                angle=angle, throttle=throttle, index=i)

            with open(os.path.join(images_dir, file_name), 'w') as outfile:
                json.dump(data, outfile)
            
            self.input = (None, None)
            self.latest_image = file_name
            
            sleep_time = self.seconds - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def get_last_index(self):
        files = next(os.walk(self.images_dir))[2]
        image_files = [f for f in files if f[:5] == 'image']

        if len(image_files) < 1:
            return 0
        
        def get_file_idx(file_name):
            name = file_name.split('.')[0]
            return int(name.split('_')[1])

        return max([get_file_idx(f) for f in image_files])