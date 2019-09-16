"""
Assorted functions for manipulating data.
"""
import itertools


def map_range(x, X_min, X_max, Y_min, Y_max):
    """
    Linear mapping between two ranges of values
    """
    X_range = X_max - X_min
    Y_range = Y_max - Y_min
    XY_ratio = X_range / Y_range

    y = ((x - X_min) / XY_ratio + Y_min) // 1

    return int(y)


def merge_two_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy
    """
    z = x.copy()
    z.update(y)
    return z


def param_gen(params):
    """
    Accepts a dictionary of parameter options and returns
    a list of dictionary with the permutations of the parameters.
    """
    for p in itertools.product(*params.values()):
        yield dict(zip(params.keys(), p ))
