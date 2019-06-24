min_uncertainty_penalty = 0.7


def neighbours(i):
    return [j for j in range(5) if abs(i - j) <= 1]


neighbours_dict = dict()
for i in range(5):
    neighbours_dict[i] = neighbours(i)

foreigners_dict = dict()
for i in range(5):
    foreigners_dict = [j for j in range(5) if j not in neighbours_dict[i]]


def uncertainty_penalty(output_keras):
    am = output_keras.argmax()
    ns = neighbours_dict[am]
    fs = foreigners_dict[am]

    res = sum([output_keras[0][i] for i in ns]) - sum([output_keras[0][i] for i in fs])
    res = max(0, res)
    res = res * (1 - min_uncertainty_penalty) + min_uncertainty_penalty

    return res


class Angle52:

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
        throttle = uncertainty_penalty(output_keras)
        return angle, throttle

    def run(self, img_arr):
        return self.postprocess(self.model.predict(self.preprocess(img_arr)))
