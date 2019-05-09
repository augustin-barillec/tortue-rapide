import logging
import yaml

def logger():
    """
    Set basic logger and return it
    """
    
    logging.basicConfig()
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.INFO)
    return _logger

def load_yaml_config(path):
    """
    Load yaml config file
    :param path: path to config file
    :return:
    """
    config_stream = open(path, "r")
    config_yaml = yaml.load(config_stream)
    return config_yaml