import glob
import json
import os
import random
from PIL import Image
import cv2

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from imgaug import augmenters as iaa
from tensorflow.python.keras.callbacks import ModelCheckpoint, EarlyStopping

from augmentation import *
from model import default_categorical
from utils import linear_bin, tub_to_array, rebalance
from config import *

save_model_path = '/home/projects/tortue-rapide/franklin_gym/test_models'

# MAP DATA PREPARATION
train_tubs = ['tub_20181113_42_afternoon',
              'tub_20181113_42_evening',
              'tub_20181124_morning_lesquare_antihoraire']
validation_tubs = ['tub_20181122_ysance_noon']

rebalance_tubs = ['tub_20181113_42_afternoon',
                  'tub_20181113_42_evening']

# 'tweak_luminosity', 'add_snow', 'add_shadow', 'add_blur', 'add_gaussian_noise', 'random_shadows'
# 'generate_night_effect', 'generate_brightness', 'generate_contrast_normalization'
augmentation_functions = ['tweak_luminosity', 'add_snow', 'add_shadows', 'add_blur']

PROPORTION = 0.2

print('import data...')
# convert tubs to numpy arrays
x_42_afternoon, y_42_afternoon = tub_to_array(tub_20181113_42_afternoon, n_class=3)
x_42_evening, y_42_evening = tub_to_array(tub_20181113_42_evening, n_class=3)
x_morning_lesquare_horaire, y_morning_lesquare_horaire = tub_to_array(tub_20181124_morning_lesquare_horaire, n_class=3)
x_morning_lesquare_antihoraire, y_morning_lesquare_antihoraire = tub_to_array(tub_20181124_morning_lesquare_antihoraire, n_class=3)
X_ysance_noon, Y_ysance_noon = tub_to_array(tub_20181122_ysance_noon, n_class=3)

# rebalance ecole 42 tubs  classes
x_42_afternoon, y_42_afternoon = rebalance(x_42_afternoon, y_42_afternoon)
x_42_evening, y_42_evening = rebalance(x_42_evening, y_42_evening)
x_morning_lesquare_horaire, y_morning_lesquare_horaire = rebalance(x_morning_lesquare_horaire, y_morning_lesquare_horaire)

# train / validation split
X_train = np.concatenate((x_42_afternoon, x_morning_lesquare_antihoraire, x_morning_lesquare_horaire, X_ysance_noon))
Y_train = np.concatenate((y_42_afternoon, y_morning_lesquare_antihoraire, y_morning_lesquare_horaire, Y_ysance_noon))
#X_val, Y_val = X_ysance_noon[:2000], Y_ysance_noon[:2000]


print('augment data...')
print('functions to be used :')
print(augmentation_functions)
print('before augmentation train data = {} samples'.format(len(X_train)))

for augment in augmentation_functions:
    print(augment)
    try:
        f = transform_dict[augment]
        X_transfo, Y_transfo = transform(X_train, Y_train, transformation=f, proportion=PROPORTION)
        X_train = np.concatenate((X_train, X_transfo))
        Y_train = np.concatenate((Y_train, Y_transfo))
    except:
        print('augmentation function not found')

print('after augmentation train data = {} samples'.format(len(X_train)))

# fit model

epochs = 100
steps = 100
verbose = 1
min_delta = .0005
patience = 8
use_early_stop = True

model = default_categorical()

# checkpoint to save model after each epoch
save_best = ModelCheckpoint(save_model_path,
                            monitor='val_loss',
                            verbose=verbose,
                            save_best_only=True,
                            mode='min')

# stop training if the validation error stops improving.
early_stop = EarlyStopping(monitor='val_loss',
                           min_delta=min_delta,
                           patience=patience,
                           verbose=verbose,
                           mode='auto')

callbacks_list = [save_best]

if use_early_stop:
    callbacks_list.append(early_stop)

model.summary()

print('fit model...')
# fit from numpy array
hist = model.fit(x=X_train,
                 y=Y_train,
                 epochs=epochs,
                 validation_split=0.25,
                 verbose=1,
                 shuffle=True,
                 callbacks=callbacks_list)

