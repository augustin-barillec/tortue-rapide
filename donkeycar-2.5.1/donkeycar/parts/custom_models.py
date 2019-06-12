from collections import deque


def ones(q):
    m = 0
    for i in q:
        if i == 1:
            m += 1
    return m


class Angle5FlipSharpThrottleOn:

    def __init__(self, model):
        self.model = model
        self.last_decisions = deque([1]*10,maxlen=10)
        self.coef = [0.98,0.99,0.995,1,1,1,1,1.02,1.03,1.05]
        self.last_throttle = 0.5

    def run(self, img_arr):
        img_arr = img_arr / 255 - 0.5
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        angle_binned = self.model.predict(img_arr)
        angle, throttle = angle_binned.argmax() * 2 / (5 - 1) - 1,self.last_throttle
        if abs(angle) == 1:
            self.last_decisions.append(0.98)
        elif angle == 0:
            self.last_decisions.append(1.005)
        else:
            self.last_decisions.append(0.995)
        if ones(self.last_decisions) < 5:
            z=zip(self.last_decisions,self.coef)
            for deci,coef in z:
                pond = deci * coef
                throttle*= pond
        if throttle>1:
            throttle=1
        if throttle < 0.4:
            throttle = 0.4
        self.last_throttle = throttle
        return angle, throttle


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
            throttle = 0.5
        elif -0.6 <= angle < -0.2:
            throttle = 0.8
        elif -0.2 <= angle < 0.2:
            throttle = 1
        elif 0.2 <= angle < 0.6:
            throttle = 0.8
        elif 0.6 <= angle:
            throttle = 1
        return angle, throttle
