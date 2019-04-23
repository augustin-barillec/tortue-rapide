import os
import time
import json
from threading import Thread

class Car():
    def __init__(self, seconds):
        self.input = (None, None)
        self.thread = Thread(target=self.record_images)
        self.thread.start()
        self.seconds = seconds
        self.is_recording = False

    def record_images(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        images_dir = os.path.join(current_dir, "images")
        file_pattern = "image_{index}_{angle}_{throttle}"

        i = 0
        while True:
            if not self.is_recording:
                continue
            
            angle, throttle = self.input
            i += 1
            if angle is None or throttle is None:
                continue


            start_time = time.time()

            data = {'ts': start_time}

            angle, throttle = self.input
            file_name = file_pattern.format(
                angle=angle, throttle=throttle, index=i)

            with open(os.path.join(images_dir, file_name), 'w') as outfile:
                json.dump(data, outfile)
            
            
            sleep_time = self.seconds - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)
