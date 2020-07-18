"""Converts images to TFRecords file format with Example protos."""

import os
import tensorflow as tf

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def convertImagesToTFRecordsFile(images, labels, shapes, directorys, name):
    num_examples = labels.shape[0]
    print('labels shape is: ', labels.shape[0])
    if num_examples != images.shape[0] != labels.shape[0]:
        raise ValueError("Images size %d does not match label size %d." %
                                         (images.shape[0], num_examples))

    filename = os.path.join(directorys, name + '.tfrecords')
    print('Writing', filename)
    writer = tf.python_io.TFRecordWriter(filename)
    for index in range(num_examples):
        image_raw = images[index].tostring()
        image_shape = shapes[index]
        example = tf.train.Example(features=tf.train.Features(feature={
                'height': _int64_feature(int(image_shape[0])),
                'width': _int64_feature(int(image_shape[1])),
                'depth': _int64_feature(int(image_shape[2])),
                'label': _int64_feature(int(labels[index])),
                'image_raw': _bytes_feature(image_raw)}))
        writer.write(example.SerializeToString())

def convertImagesToTFRecordsFile3D(images, labels, shapes, directorys, name):
    num_examples = labels.shape[0]
    print('labels shape is: ', labels.shape[0])
    if num_examples != images.shape[0] != labels.shape[0]:
        raise ValueError("Images size %d does not match label size %d." %
                                         (images.shape[0], num_examples))

    filename = os.path.join(directorys, name + '.tfrecords')
    print('Writing', filename)
    writer = tf.python_io.TFRecordWriter(filename)
    for index in range(num_examples):
        image_raw = images[index].tostring()
        image_shape = shapes[index]
        example = tf.train.Example(features=tf.train.Features(feature={
                'depth': _int64_feature(int(image_shape[0])),
                'width': _int64_feature(int(image_shape[1])),
                'height': _int64_feature(int(image_shape[2])),
                'channel': _int64_feature(int(image_shape[3])),
                'label': _int64_feature(int(labels[index])),
                'image_raw': _bytes_feature(image_raw)}))
        writer.write(example.SerializeToString())

if __name__ == '__main__':
    tf.app.run()
