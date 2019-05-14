
import json
import os
from PIL import Image
import numpy as np
import os
from glob import glob
from imageio import imread

from tensorflow.python.keras.utils import Sequence


def linear_bin(a, n_class):
    """
    Convert a value to a categorical array.

    Parameters
    ----------
    a : float
        A value between -1 and 1

    Returns
    -------
    list of int
        A list of length n_class with one item set to 1, which represents the linear value, and all other items set to 0.
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
    pics_list = glob(tub_path + '/*.jpg')
    records_list = glob(tub_path + "/record_*.json")

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

    # y = {'angle_float': np.asarray(y_angle),
    #      'throttle_out': np.asarray(y_throttle)}

    angle_categorical = []
    for n in y_angle:
        angle_categorical.append(linear_bin(n, n_class))

    # y['angle_cat_out'] = np.asarray(angle_categorical)

    return x, np.asarray(angle_categorical)



def rebalance(X, Y, replace=False):
    """
    Rebalance classes by undersampling on the over represented classes

    X : numpy array image
    Y : must by numpy array of length 3 eg [1, 0, 0]
    """
    left = np.array([np.array_equal(a, np.array([1, 0, 0])) for a in Y])
    center = np.array([np.array_equal(a, np.array([0, 1, 0])) for a in Y])
    right = np.array([np.array_equal(a, np.array([0, 0, 1])) for a in Y])

    index = np.array(range(len(Y)))
    n_wings = min(sum(left), sum(right))
    n_center = int(n_wings * 1.4) # 1.4 from observed data

    center_classes = np.random.choice(index[center], size=n_center, replace=replace)
    right_classes = np.random.choice(index[right], size=n_wings, replace=replace)
    left_classes = np.random.choice(index[left], size=n_wings, replace=replace)

    to_keep = np.concatenate((center_classes, right_classes, left_classes))

    return X[to_keep], Y[to_keep]


def generate_verified_tub_from_indexes(original_tub_path, new_tub_path, verified_indexes):
    """
    Generate new verified tub from old tub path and verified index of files

    original_tub_path {str} : old tub dir path
    new_tub_path {str} : new tub dir path to be created
    verified_indexes {list} : list of image/record indexes to keep, refering to file names indexes.
        eg : 1005 to keep 1005_cam-image_array_.jpg and 1005_record.json"""
    import shutil

    if not os.path.exists(new_tub_path):
        os.makedirs(new_tub_path)
    if not os.path.exists(os.path.join(new_tub_path, 'meta.json')):
        shutil.copy(os.path.join(original_tub_path, 'meta.json'), new_tub_path)

    jpeg_paths = glob(original_tub_path + "/*.jpg")

    for jpeg_path in jpeg_paths:
        jpg_index = int(os.path.basename(jpeg_path).split('_')[0])

        if jpg_index in verified_indexes:

            image = jpeg_path
            new_image = os.path.join(new_tub_path, os.path.basename(jpeg_path))

            record = original_tub_path + 'record_' + str(jpg_index) + '.json'
            new_record = new_tub_path + 'record_' + str(jpg_index) + '.json'

            if not os.path.exists(new_image):
                shutil.copy(image, new_tub_path)
            if not os.path.exists(new_record):
                shutil.copy(record, new_tub_path)


def generate_npy_tub_from_original(tub_path, n_classes=3):
    '''
    Generate numpy array format images from original tub format and save them in ../npy_format/{tub_name}
    relative path from tub_path (as is in google drive folder)

    tub_path {str}'''
    from imageio import imread

    tub_path = os.path.normpath(tub_path)

    jpg_files = glob(os.path.join(tub_path, '*.jpg'))
    json_files = glob(os.path.join(tub_path, '*.json'))

    new_tub_path = os.path.abspath(os.path.join(tub_path, '../../npy_format', os.path.basename(tub_path)))

    if not os.path.exists(new_tub_path):
        os.makedirs(new_tub_path)

    for jpg_file in jpg_files:
        idx = os.path.basename(jpg_file).split('_')[0]
        record_file = os.path.join(tub_path, 'record_' + idx + '.json')

        x = np.array(imread(jpg_file, format='jpg'))

        with open(record_file, 'r') as f:
            record = json.load(f)
            y_angle = record['user/angle']
            # y_throttle = append(record['user/throttle'])

        y = linear_bin(y_angle, n_classes)

        np.save(file=os.path.join(new_tub_path, 'X_' + idx), arr=x)
        np.save(file=os.path.join(new_tub_path, 'y_' + idx), arr=y)


class TubTo3DGenerator(Sequence):
    '''
    Construct Keras Data generator that handle 3D image data for tortue rapide 3D conv net training
    '''

    def __init__(self, tub_path, batch_size, frames_per_stack, dim=(120, 160), n_classes=3, shuffle=False,
                 frame_jump=1):
        self.tub_path = os.path.normpath(tub_path)
        self.imgs = glob(os.path.join(self.tub_path, '*_cam-image_array_.jpg'))
        self.records = glob(os.path.join(self.tub_path, 'record_*.json'))
        self.imgs.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))
        self.records.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))
        self.frames_per_stack = frames_per_stack
        self.stack_idx = [n + frames_per_stack * frame_jump for n in list(range(len(self.imgs) - frames_per_stack))]
        self.batch_size = batch_size
        self.dim = dim
        self.n_channels = 3
        self.n_classes = n_classes
        self.shuffle = shuffle
        self.frame_jump = frame_jump
        self.on_epoch_end()

    def __len__(self):
        'Return nb of batches per epoch'
        return int(1 + (len(self.x) / self.batch_size))

    def __getitem__(self, batch_idx):
        'Return batch of images'
        indexes = self.indexes[batch_idx * self.batch_size:(batch_idx + 1) * self.batch_size]

        return self.__data_generation(indexes)

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.array(self.stack_idx)
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, indexes):
        'Generate one batch numpy arrays from tub files and batch index'
        X = np.empty((self.batch_size, self.frames_per_stack, *self.dim, self.n_channels))
        y = np.empty((self.batch_size, self.n_classes))

        for i, idx in enumerate(indexes):
            # Store class
            with open(self.records[idx], 'r') as f:
                record = json.load(f)
                y[i] = linear_bin(float(record['user/angle']), self.n_classes)
                # y_throttle = append(record['user/throttle'])

            for j, frame in enumerate(range(self.frames_per_stack)):
                # Store sample
                X[i][j] = np.array(imread(self.imgs[idx - (frame * self.frame_jump)], format='jpg'))

        return X, y


