from tortue_rapide.util.array_float import array_to_float


class CategoricalAngleEcrin:
    def __init__(self, model, nb_of_bins, preprocess_function):
        self.model = model
        self.nb_of_bins = nb_of_bins
        self.preprocess_function = preprocess_function

    def run(self, img_arr):
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        img_arr = self.preprocess_function(img_arr)
        angle_binned = self.model.predict(img_arr)
        angle = array_to_float(angle_binned, self.nb_of_bins)
        return angle, 0


