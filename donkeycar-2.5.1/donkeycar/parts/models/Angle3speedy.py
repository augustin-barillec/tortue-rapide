def acceleration_factor(n):
    if n < 3:
        return 0
    elif n > 6:
        return 4
    else:
        return n - 2


class SpeedyFranklin3choices:

    def __init__(self, model):
        self.model = model
        self.straight_in_a_row = 0

    @staticmethod
    def preprocess(img_arr):
        res = img_arr / 255 - 0.5
        res = res.reshape((1,) + res.shape)
        return res

    def postprocess(self, output_keras):
        # output keras has length 3
        index_max = output_keras.argmax()

        if index_max == 0:
            self.straight_in_a_row = 0
            angle = -1
            throttle = 0.9
        elif index_max == 1:
            self.straight_in_a_row += 1
            angle = 0
            throttle = 1 + acceleration_factor(self.straight_in_a_row) * 0.05
        else:
            self.straight_in_a_row = 0
            angle = 1
            throttle = 0.9
        return angle, throttle

    def run(self, img_arr):
        return self.postprocess(self.model.predict(self.preprocess(img_arr)))
