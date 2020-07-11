"""Plot functions
"""
import os
import logging
from logging import Logger
import numpy as np
import matplotlib.pyplot as plt
#import ipywidgets as widgets
from IPython.display import display
from PIL import Image

from .Utils import joinPath, datestamp, timestamp, setDir
from . import ConvPlotTools
from . import LabelDefinition

figs = [] # Array to contain all figures, easy to close later
#_PLOT_DIR = './myplots'

def closeAllPlots(plt):
    '''closeAllPlots: Close all plots.
    '''
    plt.close('all')

def createNewAxes(row=1, col=1, **kwargs):

    fig, axes = plt.subplots(nrows=row, ncols=col, **kwargs)
    return fig, axes

def createNewSubplot(*args, **kwargs):
    '''createNewSubplot: Create New Sub Plot(including 3d plot).
    Returns:
        axes (2d or 3d matplotlib axes): The return value.
    '''

    axes = plt.subplot(*args, **kwargs)
    return axes

def plotMyFigure(img, cmap='Greys_r'):
    """Plot an numpy array image
       img: numpy array
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(img,cmap=cmap)

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    return ax

def plotMyFigureWithLabeBtn(img, cmap='Greys_r'):
    """Plot an numpy array image
       img: numpy array
    """
    # Define save dir
    dest_dir = joinPath(LabelDefinition.PlotLabelDir, datestamp())
    setDir(dest_dir)

    # Display image
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(img,cmap=cmap)

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    # Display widget
    img_label_choose = widgets.RadioButtons(
        options=LabelDefinition.label_class_names,
        value='none',
        description='图片类别:',
        disabled=False)

    # Define callback
    def onRadioBtn(label):
        if (img.shape==LabelDefinition.LabelPatchSizeRestrict):
            label_img_name = str(LabelDefinition.class_d_label[label['new']]) \
                +'#plot_label#none#none#none#' \
                + timestamp() \
                + '#none#.tif'
            save_path = joinPath(dest_dir, label_img_name)
            print('\r' + label['new'], ' ,saved in: ', save_path)
            Image.fromarray(np.asarray(img, np.uint8)).save(save_path)
        else:
            print('Cannot label, the image size is {0} not {1}'.format(
                img.shape,
                LabelDefinition.LabelPatchSizeRestrict))
        img_label_choose.close()
        plt.close(fig)

    img_label_choose.observe(onRadioBtn, names='value')
    display(img_label_choose)
    return ax

def plotMyFigureOnAxes(ax, img, cmap='Greys_r'):
    """Plot an numpy array image on a given Axes
       :ax: Matplotlib Axes object
       :img: numpy array
    """
    im = ax.imshow(img,cmap=cmap)
    fig = ax.figure

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    return ax


def plot_conv_weights(weights, name, channels_all=True):
    """
    Plots convolutional filters
    :param weights: numpy array of rank 4
    :param name: string, name of convolutional layer
    :param channels_all: boolean, optional
    :return: nothing, plots are saved on the disk
    """
    # make path to output folder
#    plot_dir = joinPath(_PLOT_DIR, 'conv_weights')
#    plot_dir = joinPath(plot_dir, name)

    # create directory if does not exist, otherwise empty it
#    ConvPlotTools.prepare_dir(plot_dir, empty=True)

    w_min = np.min(weights)
    w_max = np.max(weights)

    channels = [0]
    # make a list of channels if all are plotted
    if channels_all:
        channels = range(weights.shape[2])

    # get number of convolutional filters
    num_filters = weights.shape[3]

    # get number of grid rows and columns
    grid_r, grid_c = ConvPlotTools.get_grid_dim(num_filters)

    # create figure and axes
    fig, axes = plt.subplots(min([grid_r, grid_c]),
                             max([grid_r, grid_c]))
    fig.suptitle(name, fontsize=20)

    # iterate channels
    for channel in channels:
        # iterate filters inside every channel
        for l, ax in enumerate(axes.flat):
            # get a single filter
            img = weights[:, :, channel, l]
            # put it on the grid
            im = ax.imshow(img, vmin=w_min, vmax=w_max, interpolation='nearest', cmap='seismic')
            # remove any labels from the axes
            ax.set_xticks([])
            ax.set_yticks([])

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    # save figure
#    plt.savefig(joinPath(plot_dir, '{}-{}.png'.format(name.replace('/','_'), channel)), bbox_inches='tight')


def plot_conv_output(conv_img, name):
    """
    Makes plots of results of performing convolution
    :param conv_img: numpy array of rank 4
    :param name: string, name of convolutional layer
    :return: nothing, plots are saved on the disk
    """
    # make path to output folder
#    plot_dir = joinPath(_PLOT_DIR, 'conv_output')
#    plot_dir = joinPath(plot_dir, name)

    # create directory if does not exist, otherwise empty it
#    ConvPlotTools.prepare_dir(plot_dir, empty=True)

    w_min = np.min(conv_img)
    w_max = np.max(conv_img)

    # get number of convolutional filters
    num_filters = conv_img.shape[3]

    # get number of grid rows and columns
    grid_r, grid_c = ConvPlotTools.get_grid_dim(num_filters)

    # create figure and axes
    fig, axes = plt.subplots(min([grid_r, grid_c]),
                             max([grid_r, grid_c]))
    fig.suptitle(name, fontsize=20)

    # iterate filters
    for l, ax in enumerate(axes.flat):
        # get a single image
        img = conv_img[0, :, :,  l]
        # put it on the grid
        im = ax.imshow(img, vmin=w_min, vmax=w_max, interpolation='bicubic', cmap='Greys_r')
        # remove any labels from the axes
        ax.set_xticks([])
        ax.set_yticks([])

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    # save figure
#    plt.savefig(joinPath(plot_dir, '{}.png'.format(name)), bbox_inches='tight')

def isTiffFile(name):
    if not name: return False

    name_parts = name.split('.')
    if len(name_parts) != 2: return False

    str_cnt = name_parts[0]
    str_end = name_parts[1]
    if str_end != 'tif': return False

    try:
        int(str_cnt)
    except ValueError as e:
        print(e)
        return False
    else:
        return True


def readImageSequence(dir):
    img_stack = []
    try:
        if not os.path.exists(dir):
            raise IOError('image dir not exist')
        img_names = os.listdir(dir)
        img_names = list(filter(isTiffFile, img_names))
        img_names = sorted(img_names, key=lambda x:int(x.split('.')[0]))
        for img_name in img_names:
            img_path = joinPath(dir, img_name)
            try:
                im = Image.open(img_path)
                im = np.asarray(im)
                img_stack.append(im)
            except IOError as e:
                print(e)
        return np.asarray(img_stack)
    except IOError as e:
        print(e)
    finally:
        if len(img_stack)==0:
            print('no valid image sequence')
            return None
        else:
            return np.asarray(img_stack)
