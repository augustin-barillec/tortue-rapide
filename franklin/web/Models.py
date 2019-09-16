"""Holds a list of models from the exiting hdf5 files. Can refresh itself."""
import os

class Models():

    def __init__(self, directory):
        self.directory = directory
        self.models = self.get_models()


    def get_models(self):
        """Crawls the models directory and returns all the existing model files,
        as a dict {model_name: model_path}."""

        model_files = next(os.walk(self.directory))[2]
        filtered_files = filter(lambda file_name: file_name.split(".")[-1] == "hdf5", model_files)
        self.models = { ".".join(file_name.split(".")[:-1]) : "{}/{}".format(self.directory, file_name) for file_name in filtered_files }
        return self.models