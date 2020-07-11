import glob
import os
from scipy import ndimage
import tensorflow as tf
from Label import class2label


def inputPipeline(filenames,
                  batch_size,
                  num_epochs,
                  num_threads,
                  preprocess_type,
                  old_shape,
                  is_3d=False,
                  resize_type=0,
                  new_shape=None):
    filename_queue = tf.train.string_input_producer(filenames, num_epochs=num_epochs, shuffle=True)
    example, label = _readFrom(filename_queue,
                               preprocess_type,
                               old_shape,
                               resize_type,
                               new_shape,
                               is_3d=is_3d)

    #   min_after_dequeue defines how big a buffer we will randomly sample
    #   bigger means better shuffling but slower start up and more
    #   memory used.
    #   capacity must be larger than min_after_dequeue and the amount larger
    #   determines the maximum we will prefetch.  Recommendation:
    #   min_after_dequeue + (num_threads + a small safety margin) * batch_size
    min_after_dequeue = 1000
    capacity = min_after_dequeue + (num_threads+3) * batch_size
    example_batch, label_batch = tf.train.shuffle_batch(
        [example, label],
        batch_size=batch_size,
        num_threads=num_threads,
        capacity=capacity, # Ensures a minimum amount of shuffling
        min_after_dequeue=min_after_dequeue,
        name='batching_shuffing')

    return example_batch, label_batch

def _readFrom(filename_queue,
              preprocess_type,
              old_shape,
              resize_type,
              new_shape,
              is_3d):

    reader = tf.TFRecordReader()
    key, serialized_example = reader.read(filename_queue)

    features = tf.parse_single_example(
        serialized_example,
        features={'image_raw': tf.FixedLenFeature([], tf.string),
                  'label': tf.FixedLenFeature([], tf.int64)})

    image = tf.decode_raw(features['image_raw'], tf.uint8)
    image = tf.cast(image, tf.float32)
    label = tf.cast(features['label'], tf.int32)
    image = tf.reshape(image, old_shape)
    print('original image shape: ', image.get_shape())

    if not is_3d:
        if resize_type == 1:
            # do nothing
            image.set_shape(old_shape)
        elif resize_type == 2:
            # random flip
            image = tf.image.random_flip_up_down(image)
            image = tf.image.random_flip_left_right(image)
            image.set_shape(old_shape)
        elif resize_type == 3:
            # crop (0,0)
            image = tf.image.crop_to_bounding_box(image, 0, 0, new_shape[0], new_shape[1])
            image = tf.reshape(image, new_shape)
            image.set_shape(new_shape)
        elif resize_type == 4:
            # random crop
            image = tf.random_crop(image, [new_shape[0], new_shape[1], new_shape[2]])
            image = tf.reshape(image, new_shape)
            image.set_shape(new_shape)
        elif resize_type == 5:
            # random crop and random flip
            image = tf.random_crop(image, [new_shape[0], new_shape[1], new_shape[2]])
            image = tf.image.random_flip_up_down(image)
            image = tf.image.random_flip_left_right(image)
            image = tf.reshape(image, new_shape)
            image.set_shape(new_shape)
        elif resize_type == 6:
            # random crop and random flip
            image = tf.image.resize_images(image, [new_shape[0], new_shape[1]])
            image = tf.image.random_flip_up_down(image)
            image = tf.image.random_flip_left_right(image)
            image = tf.reshape(image, new_shape)
            image.set_shape(new_shape)

        if preprocess_type>0:
            image = tf.image.random_brightness(image,max_delta=63)
            image = tf.image.random_contrast(image,lower=0.2, upper=1.8)
    else:
        if resize_type == 1:  # Just resize
            # do nothing
            image.set_shape(old_shape)
        elif resize_type == 2:
            # random swap axes
            swap_axises = tf.constant([0,1,2])
            swap_axises = tf.random_shuffle(swap_axises)
            image = tf.transpose(image, perm=[swap_axises[0],
                                              swap_axises[1],
                                              swap_axises[2],
                                              3])
            image.set_shape(old_shape)
        elif resize_type == 3:
            ## Random crop
            image = tf.random_crop(image, tuple(new_shape))
            image = tf.reshape(image, new_shape)
            image.set_shape(new_shape)
        elif resize_type == 4:
            ## Random crop, flip
            image = tf.random_crop(image, tuple(new_shape))
            swap_axises = tf.constant([0,1,2])
            swap_axises = tf.random_shuffle(swap_axises)
            image = tf.transpose(image, perm=[swap_axises[0],
                                              swap_axises[1],
                                              swap_axises[2],
                                              3])
            # noise = tf.random_uniform(tuple(new_shape),minval=0,maxval=None,dtype=tf.float32)
            image = tf.reshape(image, new_shape)
            image.set_shape(new_shape)
        elif resize_type == 5:
            ## central crop
            image = tf.slice(image, [4,4,4,0], new_shape) 
            swap_axises = tf.constant([0,1,2])
            swap_axises = tf.random_shuffle(swap_axises)
            image = tf.transpose(image, perm=[swap_axises[0],
                                              swap_axises[1],
                                              swap_axises[2],
                                              3])
            image.set_shape(new_shape)


        if preprocess_type>0:
            image = tf.image.random_contrast(image,lower=0.3, upper=1.5)


    print('new image shape: ', image.get_shape())
    print('new label shape: ', label.get_shape())

    return image, label


def preprocess(array):
    # swap_axises = tf.constant([0,1,2])
    # c = tf.random_shuffle(c)
    return ndimage.rotate(array, 45)
