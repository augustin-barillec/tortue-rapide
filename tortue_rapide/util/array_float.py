import numpy


def array_to_float(a, nb_of_bins):
    return a.argmax() * 2 / (nb_of_bins - 1) - 1


def float_to_array(f, nb_of_bins):
    f += 1
    index = int(f / (2 / (nb_of_bins-1)))
    res = numpy.zeros(nb_of_bins)
    res[index] = 1
    return res
