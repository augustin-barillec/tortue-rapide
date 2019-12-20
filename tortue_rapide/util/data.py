import numpy as np
import itertools


def linear_bin(a):
    a = a + 1
    b = round(a / (2 / 14))
    arr = np.zeros(15)
    arr[int(b)] = 1
    return arr


def linear_unbin(arr):
    if not len(arr) == 15:
        raise ValueError('Illegal array length, must be 15')
    b = np.argmax(arr)
    a = b * (2 / 14) - 1
    return a


def bin_Y(Y):
    d = [linear_bin(y) for y in Y ]
    return np.array(d)


def unbin_Y(Y):
    d = [linear_unbin(y) for y in Y]
    return np.array(d)


def map_range(x, X_min, X_max, Y_min, Y_max):
    X_range = X_max - X_min
    Y_range = Y_max - Y_min
    XY_ratio = X_range / Y_range

    y = ((x - X_min) / XY_ratio + Y_min) // 1

    return int(y)


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def param_gen(params):
    for p in itertools.product(*params.values()):
        yield dict(zip(params.keys(), p ))
