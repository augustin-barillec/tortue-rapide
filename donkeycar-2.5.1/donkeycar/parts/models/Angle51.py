min_turn_penalty = 0.9
min_uncertainty_penalty = 0.7


def turn_penalty(output_keras):
    i = output_keras.argmax()
    if i in (0, 4):
        return min_turn_penalty
    elif i in (1, 3):
        return (1+min_turn_penalty)/2
    else:
        return 1


def uncertainty_penalty(output_keras):
    m = max(output_keras)
    return m*(1-min_turn_penalty) + min_turn_penalty


class Angle51:

    def __init__(self, model):
        self.model = model

    @staticmethod
    def preprocess(img_arr):
        res = img_arr / 255 - 0.5
        res = res.reshape((1,) + res.shape)
        return res

    @staticmethod
    def postprocess(output_keras):
        angle = output_keras.argmax() * 2 / (5 - 1) - 1
        throttle = turn_penalty(output_keras) * uncertainty_penalty(output_keras)
        return angle, throttle

    def run(self, img_arr):
        return self.postprocess(self.model.predict(self.preprocess(img_arr)))
