# util functions for performance evaluation

from tensorflow.python.keras.utils import to_categorical

import numpy as np
import matplotlib.pyplot as plt

def predicted_right(x_val, y_val, y_probas):
  y_hat = to_categorical(np.argmax(y_probas, axis=1))
  right_val = [np.array_equal(yhat, y) for yhat, y in zip(y_hat, y_val)]
  return np.array(right_val)

def viz_validation(x_val, y_val, y_hat):
  plt.figure(figsize=(13,40))

  for n in range(len(y_val)):
    plt.subplot(1+(len(y_val) // 4), 4, n+1)
    plt.imshow(x_val[n]+.5)
    plt.title(str(right_val[n])+'\n'+ np.array2string(np.around(y_hat[n], 3), separator=' | '))
    plt.axis('off')