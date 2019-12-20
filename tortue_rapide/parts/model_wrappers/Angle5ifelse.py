class Angle5ifelse:

    def __init__(self, model):
        self.model = model

    def run(self, img_arr):
        img_arr = img_arr / 255 - 0.5
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        angle_binned = self.model.predict(img_arr)
        angle = angle_binned.argmax() * 2 / (5 - 1) - 1

        throttle = 0
        if angle < -0.6:
            throttle = 0.8
        elif -0.6 <= angle < -0.2:
            throttle = 0.9
        elif -0.2 <= angle < 0.2:
            throttle = 1
        elif 0.2 <= angle < 0.6:
            throttle = 0.9
        elif 0.6 <= angle:
            throttle = 0.8

        return angle, throttle
