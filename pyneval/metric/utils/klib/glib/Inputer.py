import glob
import os
import numpy as np
from scipy import ndimage
from PIL import Image
import tensorflow as tf
from LabelDefinition import class_d_label
import cv2
import TiffFile
import pims

def readImageAndLabelFromFolders(paths,
                                 number=None,
                                 resized=False,
                                 new_shape=None):
    '''readImageAndLabelFromFolders
    Args:
        paths (list): List of path.
        number (list): Number of data.
        resized (bool): Whether resize.
        new_shape (2d tuple): New shape if resize.
    Returns:
        images (ndarray): Numpy array 2d image matrix.
        labels (ndarray): Numpy array of int.
        shapes (ndarray): Numpy array of 3d tuple.
    '''
    all_images = []
    all_labels = []
    all_shapes = []
    shapeset = set()

    for idx, p in enumerate(paths):
        images, labels, shapes, shape_set = readImageAndLabel(p,
                                                            number=None,
                                                            resized=False,
                                                            new_shape=None)
        print(shape_set)
        if len(shape_set)!=1:
            print('More than two image shapes, exit...')
            quit(code=-1)

        all_images.append(images)
        all_labels.append(labels)
        all_shapes.append(shapes)
        shapeset.add(shape_set.pop())

    print(shapeset)
    if len(shapeset)!=1:
        print('More than two image shapes, exit...')
        quit(code=-1)
    actual_shape = shapeset.pop()

    ret_images = np.array([], np.uint8).reshape(0, actual_shape[0], actual_shape[1], actual_shape[2])
    ret_labels = np.array([], np.uint32)
    ret_shapes = np.array([], np.int64).reshape(0,3)

    # import pdb
    # pdb.set_trace()
    for a,b,c in zip(all_images, all_labels, all_shapes):
        ret_images = np.concatenate((ret_images, a), axis=0)
        ret_labels = np.concatenate((ret_labels, b), axis=0)
        ret_shapes = np.concatenate((ret_shapes, c), axis=0)

    return ret_images, ret_labels, ret_shapes, shapeset

def readImageAndLabelFromFolders3D(paths,
                                 number=None):
    '''readImageAndLabelFromFolders
    Args:
        paths (list): List of path.
        number (list): Number of data.
        resized (bool): Whether resize.
        new_shape (2d tuple): New shape if resize.
    Returns:
        images (ndarray): Numpy array 2d image matrix.
        labels (ndarray): Numpy array of int.
        shapes (ndarray): Numpy array of 3d tuple.
    '''
    all_images = []
    all_labels = []
    all_shapes = []
    shapeset = set()

    for idx, p in enumerate(paths):
        images, labels, shapes, shape_set = readImageAndLabel3D(p,number)
        print(shape_set)
        if len(shape_set)!=1:
            print('More than two image shapes, exit...')
            quit(code=-1)

        all_images.append(images)
        all_labels.append(labels)
        all_shapes.append(shapes)
        shapeset.add(shape_set.pop())

    print(shapeset)
    if len(shapeset)!=1:
        print('More than two image shapes, exit...')
        quit(code=-1)
    actual_shape = shapeset.pop()

    ret_images = np.array([], np.uint8).reshape(0,
                                                actual_shape[0],
                                                actual_shape[1],
                                                actual_shape[2],
                                                actual_shape[3])
    ret_labels = np.array([], np.uint32)
    ret_shapes = np.array([], np.int64).reshape(0,4)

    for a,b,c in zip(all_images, all_labels, all_shapes):
        ret_images = np.concatenate((ret_images, a), axis=0)
        ret_labels = np.concatenate((ret_labels, b), axis=0)
        ret_shapes = np.concatenate((ret_shapes, c), axis=0)

    return ret_images, ret_labels, ret_shapes, shapeset

def readImageAndLabel(path, number=None,
                               resized=False, new_shape=None):
    '''read images and return image and label array
    '''

    # directories = glob.glob(os.path.join(path, '*'))
    # class_names = [os.path.basename(directory) for directory in directories]
    # class_names.sort()
    # num_classes = len(class_names)

    file_paths = glob.glob(os.path.join(path, '*/*'))
    # file_paths = sorted(file_paths,
    #        key=lambda filename:os.path.basename(filename).split('.')[0])
    np.random.shuffle(file_paths)

    images = []
    labels = []
    shapes = []
    shape_set = set()
    for file_name in file_paths[:number]:
        im = Image.open(file_name)
        if resized:
            im = im.resize(new_shape)

        im = np.asarray(im, np.uint8)
        if len(im.shape) == 2:
            im = im.reshape(im.shape[0], im.shape[1], 1)
        images.append(im)

        im_shape = im.shape
        shapes.append(im_shape)  # tuple of 3
        if im_shape not in shape_set:
            shape_set.add(im_shape)
        # image_name = os.path.basename(file_name).split('.')[0]

        class_name = os.path.basename(os.path.dirname(file_name))
        label_num = class_d_label[class_name]
        labels.append(np.asarray(label_num, np.uint32))

    images = np.array(images)
    labels = np.array(labels)
    shapes = np.array(shapes)
    print('shape set: ', shape_set)
    return images, labels, shapes, shape_set


def readImageAndLabel3D(path, number=None):
    '''read images and return image and label array 3D
    '''
    file_paths = glob.glob(os.path.join(path, '*/*'))
    np.random.shuffle(file_paths)

    images = []
    labels = []
    shapes = []
    shape_set = set()
    for file_name in file_paths[:number]:
        im = TiffFile.imread(file_name)
        # im = pims.open(file_name)
        # im = np.asarray(im, np.uint8)

        if len(im.shape) == 3:
            im = im.reshape(im.shape[0], im.shape[1], im.shape[2], 1)
        images.append(im)

        im_shape = im.shape
        shapes.append(im_shape)  # tuple of 4
        if im_shape not in shape_set:
            shape_set.add(im_shape)

        class_name = os.path.basename(os.path.dirname(file_name))
        label_num = class_d_label[class_name]
        labels.append(np.asarray(label_num, np.uint32))

    images = np.array(images)
    labels = np.array(labels)
    shapes = np.array(shapes)
    print('shape set: ', shape_set)
    return images, labels, shapes, shape_set

def inputPipeline(filenames,
                      batch_size,
                      num_epochs,
                      num_threads,
                      old_shape,
                      do_train,
                      normalize=False,
                      resize_type=0,
                      new_shape=None):
    ''' The input pipeline for TensorFlow graph
    '''
    filename_queue = tf.train.string_input_producer(
                     filenames, num_epochs=num_epochs, shuffle=True)
    if len(old_shape)==3:
        print('*'*20,'2D inputPipeline', '*'*20)
        example, label = _readImagesFromTFRecordsFile(filename_queue,
                                                               old_shape,
                                                               normalize,
                                                               do_train, # train vs eval, diff preprocess
                                                               resize_type,
                                                               new_shape)
    else:
        print('*'*20,'3D inputPipeline', '*'*20)
        example, label = _readImagesFromTFRecordsFile3D(filename_queue,
                                                               old_shape,
                                                               normalize,
                                                               do_train, # train vs eval, diff preprocess
                                                               resize_type,
                                                               new_shape)
    # min_after_dequeue defines how big a buffer we will randomly sample
    #   from -- bigger means better shuffling but slower start up and more
    #   memory used.
    # capacity must be larger than min_after_dequeue and the amount larger
    #   determines the maximum we will prefetch.  Recommendation:
    #   min_after_dequeue + (num_threads + a small safety margin) * batch_size
    min_after_dequeue = 1000
    capacity = min_after_dequeue + (num_threads+3) * batch_size
    example_batch, label_batch =  \
        tf.train.shuffle_batch([example, label],
                               batch_size=batch_size,
                               num_threads=num_threads,
                               capacity=capacity,
                               # Ensures a minimum amount of shuffling
                               min_after_dequeue=min_after_dequeue,
                               name='batching_shuffing')
    return example_batch, label_batch

def _readImagesFromTFRecordsFile(filename_queue,
                                          old_shape,
                                          normalize,
                                          do_train,
                                          resize_type,
                                          new_shape):

    reader = tf.TFRecordReader()
    key, serialized_example = reader.read(filename_queue)

    features = tf.parse_single_example(serialized_example,
                                       features={'image_raw': tf.FixedLenFeature([], tf.string),
                                                 'label': tf.FixedLenFeature([], tf.int64)
                                                })

    image = tf.decode_raw(features['image_raw'], tf.uint8)
    image = tf.cast(image, tf.float32)
    label = tf.cast(features['label'], tf.int32)
    image = tf.reshape(image, old_shape)
    image.set_shape(old_shape)
    print('original image shape: ', image.get_shape())

    if resize_type == 1:  # resize_type default 0, do nothing
        image = tf.image.rgb_to_grayscale(image)
        image = tf.image.crop_to_bounding_box(image, 0, 55, 223, 223)
        image = tf.image.resize_images(image, [new_shape[0], new_shape[1]])
        image = tf.reshape(image, new_shape)
    elif resize_type == 2:
        ''' Random crop 40by40 to 32by32
            Image is default gray
        '''
        # offset_height = np.random.randint(0, 9)
        # offset_width = np.random.randint(0, 9)
        # image = tf.image.crop_to_bounding_box(image,
        #                                       offset_height,
        #                                       offset_width,
        #                                       new_shape[0],
        #                                       new_shape[1])
        image = tf.image.crop_to_bounding_box(image,
                                              0,
                                              0,
                                              new_shape[0],
                                              new_shape[1])
        # print 'TensorFlow random crop'
        # image = tf.random_crop(image, (32, 32, 1))
        image = tf.reshape(image, new_shape)
    elif resize_type == 3:
        # image = tf.image.resize_images(image, [new_shape[0], new_shape[1]])
        # image = tf.image.crop_to_bounding_box(image,
        #                                       7,
        #                                       0,
        #                                       new_shape[0],
        #                                       new_shape[1])

        print( 'TensorFlow random crop')
        image = tf.random_crop(image, (32, 32, 1))
        image = tf.image.random_flip_up_down(image)
        image = tf.image.random_flip_left_right(image)
        if do_train:
            image = tf.image.random_brightness(image,max_delta=63)
            image = tf.image.random_contrast(image,lower=0.2, upper=1.8)
        image = tf.reshape(image, new_shape)

    print('new image shape: ', image.get_shape())
    print('label shape: ', label.get_shape())

    processed_example = image
    return processed_example, label

def preprocess(array):
    # swap_axises = tf.constant([0,1,2])
    # c = tf.random_shuffle(c)
    return ndimage.rotate(array, 45)

def _readImagesFromTFRecordsFile3D(filename_queue,
                                          old_shape,
                                          normalize,
                                          do_train,
                                          resize_type,
                                          new_shape):

    reader = tf.TFRecordReader()
    key, serialized_example = reader.read(filename_queue)

    features = tf.parse_single_example(serialized_example,
                                       features={'image_raw': tf.FixedLenFeature([], tf.string),
                                                 'label': tf.FixedLenFeature([], tf.int64)
                                                })

    image = tf.decode_raw(features['image_raw'], tf.uint8)
    image = tf.cast(image, tf.float32)
    label = tf.cast(features['label'], tf.int32)
    image = tf.reshape(image, old_shape)
    image.set_shape(old_shape)
    print('original image shape:', image.get_shape())

    ## Default 0, just resize
    if resize_type == 1:  # Just resize
        ## Don't crop, augment and resize
        swap_axises = tf.constant([0,1,2])
        swap_axises = tf.random_shuffle(swap_axises)
        image = tf.transpose(image, perm=[swap_axises[0],
                                          swap_axises[1],
                                          swap_axises[2],
                                          3])
        image = tf.reshape(image, new_shape)
    elif resize_type == 2:
        ## Random crop , flip
        image = tf.random_crop(image, tuple(new_shape))
        swap_axises = tf.constant([0,1,2])
        swap_axises = tf.random_shuffle(swap_axises)
        image = tf.transpose(image, perm=[swap_axises[0],
                                          swap_axises[1],
                                          swap_axises[2],
                                          3])
        image = tf.reshape(image, new_shape)
        image.set_shape(new_shape)
    elif resize_type == 3:
        ## Random crop, flip and adjust contrast
        image = tf.random_crop(image, tuple(new_shape))
        swap_axises = tf.constant([0,1,2])
        swap_axises = tf.random_shuffle(swap_axises)
        image = tf.transpose(image, perm=[swap_axises[0],
                                          swap_axises[1],
                                          swap_axises[2],
                                          3])
        # noise = tf.random_uniform(tuple(new_shape),minval=0,maxval=None,dtype=tf.float32)
        image = tf.image.random_contrast(image,lower=0.3, upper=1.5)
        image = tf.reshape(image, new_shape)
        image.set_shape(new_shape)

    processed_example = image
    return processed_example, label

def getLabelClassMap(base_dir):
    directories = glob.glob(os.path.join(base_dir, '*'))
    class_names = [os.path.basename(directory) for directory in directories]
    class_names.sort()
    label_d_class = dict(zip(range(len(class_names)), class_names))
    class_d_label = dict(zip(class_names, range(len(class_names))))
    return label_d_class, class_d_label
