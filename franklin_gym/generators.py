import numpy as np
from tensorflow.python.keras.utils import Sequence

from training_utils import horizontal_flip_inplace

class TortueInMemoryGenerator(Sequence):
    'Construct data iterator for in memory training that handle on the fly data augmentation with albumentations'
    def __init__(self, x_set, y_set, batch_size, augmentations, flip_proportion, shuffle=True):
        self.x, self.y = x_set, y_set
        self.indexes = np.arange(x_set.shape[0])
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.augment = augmentations
        self.flip_proportion = flip_proportion
        self.on_epoch_end()

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__(self, idx):
        indexes = self.indexes[idx * self.batch_size:(idx + 1) * self.batch_size]

        batch_x = self.x[indexes]
        batch_y = self.y[indexes]

        batch_x, batch_y = horizontal_flip_inplace(batch_x, batch_y, proportion=self.flip_proportion)

        return np.stack([
            self.augment(image=x)["image"] for x in batch_x
        ], axis=0), np.array(batch_y)

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        if self.shuffle == True:
            np.random.shuffle(self.indexes)



class TubTo3DGenerator(Sequence):
    '''
    Construct data iterator that export images batches for 3D convnet training
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

