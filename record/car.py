import os
import time
import json


class Car():
    def __init__(self):
        self.input = (None, None)
        self.is_recording = False

    def record_images(self, seconds):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        images_dir = os.path.join(current_dir, "images")
        file_pattern = "image_{angle}_{throttle}_{index}"

        i = 0
        while self.is_recording:
            angle, throttle = self.input

            if i % 1000000 == 0: print("INPUT FOR FILENAME: {}".format(self.input))
            i += 1
            if angle is None or throttle is None:
                # time.sleep(1)
                continue


            start_time = time.time()

            data = {'ts': start_time}

            angle, throttle = self.input
            file_name = file_pattern.format(
                angle=angle, throttle=throttle, index=i)

            # with open(os.path.join(images_dir, file_name), 'w') as outfile:
            #     json.dump(data, outfile)
            
            
            sleep_time = seconds - (time.time() - start_time)
            # if sleep_time > 0.0:
            #     time.sleep(sleep_time)
