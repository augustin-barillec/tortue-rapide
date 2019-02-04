
import json
import os
import glob
from PIL import Image
import numpy as np


def linear_bin(a, n_class):
    """
    Convert a value to a categorical array.

    Parameters
    ----------
    a : int or float
        A value between -1 and 1

    Returns
    -------
    list of int
        A list of length 15 with one item set to 1, which represents the linear value, and all other items set to 0.
    """
    a = a + 1
    b = round((n_class - 1) * a / 2)
    arr = np.zeros(n_class)
    arr[int(b)] = 1
    return arr


def tub_to_array(tub_path, n_class, n_first_files=None):
    """
    Return dict of Numpy arrays containing pixel images and associated values of angle and throttle from a tub path

    tub_path: str
        path of tub to convert
    n_first_files: int

    """
    pics_list = glob.glob(tub_path + '/*.jpg')
    records_list = glob.glob(tub_path + "/record_*.json")

    pics_list.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))
    records_list.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))

    pics_list = pics_list[:n_first_files]
    records_list = records_list[:n_first_files]

    meta_path = tub_path + "/meta.json"

    x = np.array([np.array(Image.open(fname)) for fname in pics_list])
    y_angle = []
    y_throttle = []
    for file in records_list:
        with open(file, 'r') as f:
            record = json.load(f)
            y_angle.append(record['user/angle'])
            y_throttle.append(record['user/throttle'])

    y = {'angle_float': np.asarray(y_angle),
         'throttle_out': np.asarray(y_throttle)}

    res = []
    for n in y['angle_float']:
        res.append(linear_bin(n, n_class))

    y['angle_cat_out'] = np.asarray(res)

    return x, y