import io
import os

from PIL import Image
import numpy as np


def scale(im, size=128):
    size = (size,size)
    im.thumbnail(size, Image.ANTIALIAS)
    return im


def img_to_binary(img):
    f = io.BytesIO()
    img.save(f, format='jpeg')
    return f.getvalue()


def arr_to_binary(arr):
    img = arr_to_img(arr)
    return img_to_binary(img)


def arr_to_img(arr):
    arr = np.uint8(arr)
    img = Image.fromarray(arr)
    return img


def img_to_arr(img):
    return np.array(img)


def binary_to_img(binary):
    img = io.BytesIO(binary)
    return Image.open(img)


def norm_img(img):
    return (img - img.mean() / np.std(img))/255.0


def create_video(img_dir_path, output_video_path):
    import envoy
    # Setup path to the images with telemetry.
    full_path = os.path.join(img_dir_path, 'frame_*.png')

    # Run ffmpeg.
    command = ("""ffmpeg
               -framerate 30/1
               -pattern_type glob -i '%s'
               -c:v libx264
               -r 15
               -pix_fmt yuv420p
               -y
               %s""" % (full_path, output_video_path))
    response = envoy.run(command)
