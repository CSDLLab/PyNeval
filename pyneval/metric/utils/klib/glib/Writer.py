"""Converts images to TFRecords file format with Example protos."""

import os
import sys
import glob
import json
import tensorflow as tf
from PIL import Image
import tifffile
import numpy as np
import Utils
from Label import class2label

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _readFolders(
    input_path,
    class_label_file_path,
    organize_type,
    resize,
    new_size,
	is_3d,
    number):

    class_2_label = Utils.json2dict(class_label_file_path)
    im_shape = []
    if organize_type==3:
        file_paths = glob.glob(os.path.join(input_path, '*'))
    else:
        file_paths = glob.glob(os.path.join(input_path, '*/*'))

    np.random.shuffle(file_paths)
    try:
        for file_name in file_paths:
            if is_3d:
                im = tifffile.imread(file_name)
            else:
                im = Image.open(file_name)
            if resize:
                im = im.resize(new_size)

            im = np.asarray(im, np.uint8)
            if len(im.shape)==2:
                im = im.reshape(im.shape[0], im.shape[1], 1)
            elif len(im.shape)==3:
                im = im.reshape(im.shape[0], im.shape[1], im.shape[2], 1)
            else:
                continue
            # check shape
            if len(im_shape)>0 and im_shape[0]!=im.shape:
                sys.exit('input image size not same')
            else:
                if len(im_shape)==0:
                    im_shape.append(im.shape)
                else:
                    im_shape[0] = im.shape

            if organize_type==1:
                class_name = os.path.basename(os.path.dirname(file_name))
            elif organize_type==2:
                class_name = os.path.basename(file_name).split('-')[0]
            elif organize_type==3:
                # don't care label, for gan train
                class_name = 'branch'
            else:
                sys.exit('organize type error')

            global result
            if class_name in class_2_label:
            	label = class_2_label[class_name]
            else:
                continue

            if class_name not in result:
                result[class_name] = 1
            else:
                result[class_name] += 1

            yield im, label

    except IOError as e:
        sys.exit('image read error')

    print('summary: input image shape is: ', im_shape[0])


def convertTo(
    input_path_list,
    output_path,
    class_label_file_path,
    organize_type,
	is_3d=False,
	resize=False,
    new_size=None,
    number=None):
    ''' create tfrecords file
        input_path_list (string)
        output_path (string) : tfrecords output file path
        organize_type (int) : 1->organize by folder, 2->organize in one folder, 3->don't care label for gan
        is_3d (bool) : is input image 3d
    '''
    global result
    result = dict()
    writer = tf.python_io.TFRecordWriter(output_path)
    for input_path in input_path_list:
        for image, label in _readFolders(
            input_path,
            class_label_file_path,
            organize_type,
			resize,
			new_size,
            is_3d,
            number):
            image_raw = image.tostring()
            image_shape = image.shape
            if is_3d:
                example = tf.train.Example(
                    features=tf.train.Features(
                        feature={
                            'depth': _int64_feature(int(image_shape[0])),
                            'width': _int64_feature(int(image_shape[1])),
                            'height': _int64_feature(int(image_shape[2])),
                            'channel': _int64_feature(int(image_shape[3])),
                            'label': _int64_feature(int(label)),
                            'image_raw': _bytes_feature(image_raw)
                            }
                        )
                    )
            else:
                example = tf.train.Example(
                    features=tf.train.Features(
                        feature={
                            'height': _int64_feature(image_shape[0]),
                            'width': _int64_feature(image_shape[1]),
                            'depth': _int64_feature(image_shape[2]),
                            'label': _int64_feature(label),
                            'image_raw': _bytes_feature(image_raw)
                            }
                        )
                    )

            writer.write(example.SerializeToString())

    return result

if __name__ == '__main__':
    tf.app.run()
