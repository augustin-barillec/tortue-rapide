import time
from threading import Thread

from picamera.array import PiRGBArray
from picamera import PiCamera

class Camera():
    def __init__(self):
        resolution = (160, 120)
        # initialize the camera and stream
        self.camera = PiCamera()  # PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        self.camera.framerate = 20
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="rgb",
                                                     use_video_port=True)

        self.frame = None
        self.run = True
        
        print('Camera started, warming up...')
        time.sleep(2)

        self.thread = Thread(target=self.consume)
        self.thread.start()

    def consume(self):
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
            
            if not self.run:
                break

    # def shutdown(self):
    #     # indicate that the thread should be stopped
    #     self.on = False
    #     print('stoping PiCamera')
    #     time.sleep(.5)
    #     self.stream.close()
    #     self.rawCapture.close()
    #     self.camera.close()