import cv2
import numpy as np
import random
import skimage.exposure as sk
from tqdm import tqdm
from imgaug import augmenters as iaa


def augment_brightness_camera_images(image, angle):
    '''Random bright augmentation (both darker and brighter).
    
    Returns:
    Transformed image and label.
    '''
    image1 = cv2.cvtColor(image,cv2.COLOR_RGB2HSV)
    image1 = np.array(image1, dtype = np.float64)
    random_bright = .5+np.random.uniform()
    image1[:,:,2] = image1[:,:,2]*random_bright
    image1[:,:,2][image1[:,:,2]>255]  = 255
    image1 = np.array(image1, dtype = np.uint8)
    image1 = cv2.cvtColor(image1,cv2.COLOR_HSV2RGB)
    return image1, angle


def add_random_shadow(image, angle):
    '''Add random dark shadows to a given image.

    Returns:
    Transformed image and label.
    '''
    top_x = 0
    bot_x = 160

    top_y = 320*np.random.uniform()
    bot_y = 320*np.random.uniform()

    image_hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)

    shadow_mask = 0*image_hls[:,:,1]
    X_m = np.mgrid[0:image.shape[0],0:image.shape[1]][0]
    Y_m = np.mgrid[0:image.shape[0],0:image.shape[1]][1]
    shadow_mask[((X_m-top_x)*(bot_y-top_y) -(bot_x - top_x)*(Y_m-top_y) >=0)]=1
    #random_bright = .25+.7*np.random.uniform()
    if np.random.randint(2)==1:
        random_bright = .5
        cond1 = shadow_mask==1
        cond0 = shadow_mask==0
        if np.random.randint(2)==1:
            image_hls[:,:,1][cond1] = image_hls[:,:,1][cond1]*random_bright
        else:
            image_hls[:,:,1][cond0] = image_hls[:,:,1][cond0]*random_bright    
    image = cv2.cvtColor(image_hls,cv2.COLOR_HLS2RGB)
    return image, angle


def night_effect(img,  label, vmin=185, vmax=195):
    """Change road color to black simulating night road.

    Returns
    Transformed image and label.
    """
    limit = random.uniform(vmin,vmax)
    low_limit = 146 
    int_img = sk.rescale_intensity(img, in_range=(low_limit,limit), out_range='dtype')
    
    return int_img, label


def adjust_gamma_dark(image, label, min_=0.7, max_=0.8):
    '''Gamma correction to generate darker images.

    Image: Image in Numpy format (90,250,3)
    Label: Corresponding label of the image.
    Min: Minimum gamma value (the lower the darker)
    Max: Maximum gamma value (the higher the brigther) 
    Return:
    Transformed image and label.
    '''
    # build a lookup table mapping the pixel values [0, 255] to
    gamma = random.uniform(min_,max_)
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table), label



def generate_brightness(X, Y, proportion=0.25):
    '''Image augmentation changing the intensity randomly.

    X: Numpy array of training images in channels-last format.
    Y: Labels (array of 5 elements).
    proportion: percentage of elements to be generated (25% of total by default).
    Returns
    X_aug: Numpy tensor of images according to the desired proportion.
    Y_aug: Numpy tensor of labels for each image.
    '''
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0]*proportion))
    
    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        # Apply the desired transformation
        im, angle = augment_brightness_camera_images(X[index], Y[index])
        Y_aug.append(angle)
        X_aug.append(im)

    return X_aug, Y_aug


def generate_low_gamma(X, Y, proportion=0.25):
    '''Image augmentation by lowering the gamma (darker images).

    X: Numpy array of training images in channels-last format.
    Y: Labels (array of 5 elements).
    proportion: percentage of elements to be generated (25% of total by default).
    Returns
    X_aug: Numpy tensor of images according to the desired proportion.
    Y_aug: Numpy tensor of labels for each image.
    '''
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0]*proportion))
    
    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        # Apply the desired transformation
        im, angle = adjust_gamma_dark(X[index], Y[index])
        Y_aug.append(angle)
        X_aug.append(im)

    return X_aug, Y_aug


def generate_night_effect(X, Y, proportion=0.25):
    '''Image augmentation with night effect (black track).

    X: Numpy array of training images in channels-last format.
    Y: Labels (array of 5 elements).
    proportion: percentage of elements to be generated (25% of total by default).
    Returns
    X_aug: Numpy tensor of images according to the desired proportion.
    Y_aug: Numpy tensor of labels for each image.
    '''
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0]*proportion))
    
    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        # Apply the desired transformation
        im, angle = night_effect(X[index], Y[index])
        Y_aug.append(angle)
        X_aug.append(im)

    return X_aug, Y_aug


def generate_horizontal_flip(X, Y, proportion=0.25):
    '''Image augmentation by lowering the gamma (darker images).

    X: Numpy array of training images in channels-last format.
    Y: Labels MUST be a 5-elements array.
    proportion: percentage of elements to be generated (25% of total by default).
    Returns
    X_aug: Numpy tensor of images according to the desired proportion.
    Y_aug: Numpy tensor of labels for each image.
    '''
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0]*proportion))
    
    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        # Apply the desired transformation
        im, angle = horizontal_flip(X[index], Y[index])
        Y_aug.append(angle)
        X_aug.append(im)

    return X_aug, Y_aug


def generate_random_shadows(X, Y, proportion=0.25):
    '''Image augmentation by lowering the gamma (darker images).

    X: Numpy array of training images in channels-last format.
    Y: Labels MUST be a 5-elements array.
    proportion: percentage of elements to be generated (25% of total by default).
    Returns
    X_aug: Numpy tensor of images according to the desired proportion.
    Y_aug: Numpy tensor of labels for each image.
    '''
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0]*proportion))
    
    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        # Apply the desired transformation
        im, angle = add_random_shadow(X[index], Y[index])
        Y_aug.append(angle)
        X_aug.append(im)

    return X_aug, Y_aug


def generate_chained_transformations(X, Y, proportion=0.25):
    '''Image augmentation applying brightness + shadow + random flipping.

    X: Numpy array of training images in channels-last format.
    Y: Labels MUST be a 5-elements array.
    proportion: percentage of elements to be generated (25% of total by default).
    Returns
    X_aug: Numpy tensor of images according to the desired proportion.
    Y_aug: Numpy tensor of labels for each image.
    '''
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0]*proportion))
    
    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        # Apply the desired transformation
        im, angle = augment_brightness_camera_images(X[index], Y[index])
        im, angle =  add_random_shadow(im, angle)
    
        if index%2==0:
            im, angle = horizontal_flip(im, angle)
        Y_aug.append(angle)
        X_aug.append(im)
    
    return X_aug, Y_aug



def generate_shadow_coordinates(imshape, no_of_shadows=1):
    vertices_list = []
    for index in range(no_of_shadows):
        vertex = []
        for dimensions in range(np.random.randint(3, 15)):  ## Dimensionality of the shadow polygon
            vertex.append((imshape[1] * np.random.uniform(), imshape[0] // 3 + imshape[0] * np.random.uniform()))
        vertices = np.array([vertex], dtype=np.int32)  ## single shadow vertices
        vertices_list.append(vertices)
    return vertices_list  ## List of shadow vertices


##


def tweak_luminosity(image):
    image_HLS = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)  ## Conversion to HLS
    random_brightness_coefficient = np.random.uniform() + 0.5  ## generates value between 0.5 and 1.5
    image_HLS[:, :, 1] = image_HLS[:, :,
                         1] * random_brightness_coefficient  ## scale pixel values up or down for channel 1(Lightness)
    image_HLS[:, :, 1][image_HLS[:, :, 1] > 255] = 255  ##Sets all values above 255 to 255
    image_HLS = np.array(image_HLS, dtype=np.uint8)
    image_RGB = cv2.cvtColor(image_HLS, cv2.COLOR_HLS2RGB)
    return image_RGB


def add_snow(image):
    image_HLS = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)  ## Conversion to HLS
    image_HLS = np.array(image_HLS, dtype=np.float64)
    brightness_coefficient = 2.5
    snow_point = 60  ## increase this for more snow
    image_HLS[:, :, 1][image_HLS[:, :, 1] < snow_point] = image_HLS[:, :, 1][image_HLS[:, :,
                                                                             1] < snow_point] * brightness_coefficient  ## scale pixel values up for channel 1(Lightness)
    image_HLS[:, :, 1][image_HLS[:, :, 1] > 255] = 255  ##Sets all values above 255 to 255
    image_HLS = np.array(image_HLS, dtype=np.uint8)
    image_RGB = cv2.cvtColor(image_HLS, cv2.COLOR_HLS2RGB)  ## Conversion to RGB
    return image_RGB


def shadow_coordinates(imshape, no_of_shadows=2):
    vertices_list = []
    for index in range(no_of_shadows):
        vertex = []
        for dimensions in range(np.random.randint(3, 15)):  ## Dimensionality of the shadow polygon
            vertex.append((imshape[1] * np.random.uniform(), imshape[0] // 3 + imshape[0] * np.random.uniform()))
        vertices = np.array([vertex], dtype=np.int32)  ## single shadow vertices
        vertices_list.append(vertices)
    return vertices_list  ## List of shadow vertices


def add_shadows(image, no_of_shadows=2):
    image_HLS = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)  ## Conversion to HLS
    mask = np.zeros_like(image)
    imshape = image.shape
    vertices_list = shadow_coordinates(imshape, no_of_shadows)  # 3 getting list of shadow vertices
    for vertices in vertices_list:
        cv2.fillPoly(mask, vertices,
                     255)  ## adding all shadow polygons on empty mask, single 255 denotes only red channel

    image_HLS[:, :, 1][mask[:, :, 0] == 255] = image_HLS[:, :, 1][mask[:, :,
                                                                  0] == 255] * 0.5  ## if red channel is hot, image's "Lightness" channel's brightness is lowered
    image_RGB = cv2.cvtColor(image_HLS, cv2.COLOR_HLS2RGB)  ## Conversion to RGB
    return image_RGB


def add_blur(images):
    seq = iaa.Sequential([
        iaa.GaussianBlur(sigma=(0, 3.0))  # blur images with a sigma of 0 to 3.0
    ])

    aug_images = seq.augment_image(images)

    return aug_images


def add_gaussian_noise(images):
    seq = iaa.Sequential([
        iaa.AdditiveGaussianNoise(scale=(0, 0.08 * 255))
    ])

    aug_images = seq.augment_image(images)

    return aug_images


def add_contrast_normalization(images):
    seq = iaa.Sequential([
        iaa.ContrastNormalization((0.2, 1.5))
    ])

    aug_images = seq.augment_image(images)

    return aug_images


def transform(X, Y, transformation, proportion=0.25):
    # Generate a random selection of indexes
    indexes = random.sample(range(0, X.shape[0]), int(X.shape[0] * proportion))

    X_aug = []
    Y_aug = []
    for index in tqdm(indexes):
        im = transformation(X[index])
        X_aug.append(im)
        Y_aug.append(Y[index])

    return np.asarray(X_aug), np.asarray(Y_aug)


# augmentation dict
transform_dict = {
    'tweak_luminosity': tweak_luminosity,
    'add_snow': add_snow,
    'add_blur': add_blur,
    'add_gaussian_noise': add_gaussian_noise,
    'add_shadows': add_shadows,
    'add_contrast_normalization': add_contrast_normalization
}
