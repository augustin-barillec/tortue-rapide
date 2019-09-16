class Angle3ifelse:

    def __init__(self, model):
        self.model = model

    def run(self, img_arr):
        img_arr = img_arr / 255 - 0.5
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        angle_binned = self.model.predict(img_arr)
        index_max = angle_binned.argmax()

        if index_max == 0:
            angle = -1
            throttle = 0.9
        elif index_max == 1:
            angle = 0
            throttle = 1
        else:
            angle = 1
            throttle = 0.9

        return angle, throttle

