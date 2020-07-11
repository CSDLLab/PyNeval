# @Author: guanwanxian
# @Date:   1970-01-01T08:00:00+08:00
# @Email:  guanwanxian@zju.edu.cn
# @Last modified by:   guanwanxian
# @Last modified time: 2017-11-14T20:47:21+08:00

"""ImageUtils, providing basic functions for drawing synthesized microscopic images
"""

from enum import Enum
import numpy as np


def normalizeImage(im):
    im = np.asarray(im, np.float)
    im = np.where(im>255, 255, im)
    im = np.where(im<0, 0, im)
    #im = (im-im.min())*255.0/(im.max()-im.min())
    #im = im.astype(np.uint8)
    return im

def bboxCheck3D(z,y,x,R,img_shape):
    '''bboxCheck: Chech box inside image.
    Args:
        x (float): x pos
        y (float): y pos
        z (float): z pos
        R (int): box radius
        img_shape ((int,int,int)): image shape
    Returns:
        (bool).
    '''
    return (z-R>=0 and z+R<=img_shape[0] and y-R>=0 and y+R<=img_shape[1] and x-R>=0 and x+R<=img_shape[2])

def bboxCheck3DSeparate(z,y,x,rz,ry,rx,img_shape):
    '''bboxCheck: Chech box inside image.
    Args:
        x (float): x pos
        y (float): y pos
        z (float): z pos
        R (int): box radius
        img_shape ((int,int,int)): image shape
    Returns:
        (bool).
    '''
    return (z-rz>=0 and z+rz<=img_shape[0] and y-ry>=0 and y+ry<=img_shape[1] and x-rx>=0 and x+rx<=img_shape[2])

class ImgType(Enum):
    NonBranch = 1
    Branch = 2

class OpType(Enum):

    GetIndex = 1

    GenerateImage = 2

    GetBlackIndex = 3

    GenerageBlackImage = 4

def noisyAddGray(noise_typ,image, op_type):
    """
    Parameters
    ----------
    image : ndarray
        Input image data. Will be converted to float.
    mode : str
        One of the following strings, selecting the type of noise to add:

        'gauss'     Gaussian-distributed additive noise.
        'poisson'   Poisson-distributed noise generated from the data.
        's&p'       Replaces random pixels with 0 or 1.
        'speckle'   Multiplicative noise using out = image + n*image,where
                    n is uniform noise with specified mean & variance.
    """
    if noise_typ == "gauss":
        row,col= image.shape
        mean = 0
        if op_type == OpType.GenerateImage:
            var = 0.1
        elif op_type == OpType.GenerageBlackImage:
            var = 0.1 * np.random.randint(3,6)
        else:
            print('Wrong type, add gauss noise')

        sigma = var**0.5
        gauss = np.random.normal(mean,sigma,(row,col))
        gauss = gauss.reshape(row,col)
        noisy = image + gauss
        return noisy

    elif noise_typ == "s&p":
        avg_intensity = np.asarray(image).mean()
        row,col = image.shape
        s_vs_p = 0.5
        amount = 0.05
        out = image.copy()
        # Salt mode
        num_salt = np.ceil(amount * image.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in image.shape]

        if op_type == OpType.GenerateImage:
            out[coords] = np.where(out[coords]*1.1>255, 255, out[coords]*1.1)
        elif op_type == OpType.GenerageBlackImage:
            out[coords] = np.where(out[coords]*1.5>255, 255, out[coords]*1.5)
        else:
            print('Wrong type, add s&p noise')


        # Pepper mode
        num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
              for i in image.shape]
        if op_type == OpType.GenerateImage:
            out[coords] = np.where(out[coords]>avg_intensity, out[coords]*0.8, out[coords]*0.1)
        elif op_type == OpType.GenerageBlackImage:
            out[coords] = np.where(out[coords]>avg_intensity, out[coords]*0.6, out[coords]*0.1)
        else:
            print('Wrong type, add s&p noise')

        return out

    elif noise_typ == "poisson":
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(image * vals) / float(vals)
        return noisy

    elif noise_typ =="speckle":
        row,col = image.shape
        gauss = np.random.randn(row,col)
        gauss = gauss.reshape(row,col)

        if op_type == OpType.GenerateImage:
            grade = np.random.randint(1,6)
        elif op_type == OpType.GenerageBlackImage:
            grade = np.random.randint(6,20)
        else:
            print('Wrong type, add speckle noise')

        noisy = image + image * gauss * 0.01 * grade
        return noisy

def gaussianNoisyAddGray3D(image,mean,std):
    row,col,dep= image.shape
    gauss = np.random.normal(mean,std,(row,col,dep))
    gauss = gauss.reshape(row,col,dep)
    noisy = image + gauss
    noisy = normalizeImage(noisy)
    return noisy

def noisyAddGray3D(noise_typ,image):
    """
    Parameters
    ----------
    image : ndarray
        Input image data. Will be converted to float.
    mode : str
        One of the following strings, selecting the type of noise to add:

        'gauss'     Gaussian-distributed additive noise.
        'poisson'   Poisson-distributed noise generated from the data.
        's&p'       Replaces random pixels with 0 or 1.
        'speckle'   Multiplicative noise using out = image + n*image,where
                    n is uniform noise with specified mean & variance.
    """
    if noise_typ == "gauss":
        row,col,dep= image.shape
        mean = 40
        sigma = 2#np.random.randint(10,20)
        gauss = np.random.normal(mean,sigma,(row,col,dep))
        gauss = gauss.reshape(row,col,dep)
        noisy = image + gauss
        # 标准化到0-255
        noisy = normalizeImage(noisy)
        return noisy
    elif noise_typ == "poisson":
        noisy = np.random.poisson(lam=image,size=None)
        # 标准化到0-255
        noisy = normalizeImage(noisy)
        return noisy
    elif noise_typ == "s&p":
        avg_intensity = np.asarray(image).mean()
        row,col = image.shape
        s_vs_p = 0.5
        amount = 0.05
        out = image.copy()
        # Salt mode
        num_salt = np.ceil(amount * image.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in image.shape]

        if op_type == OpType.GenerateImage:
            out[coords] = np.where(out[coords]*1.1>255, 255, out[coords]*1.1)
        elif op_type == OpType.GenerageBlackImage:
            out[coords] = np.where(out[coords]*1.5>255, 255, out[coords]*1.5)
        else:
            print('Wrong type, add s&p noise')


        # Pepper mode
        num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
              for i in image.shape]
        if op_type == OpType.GenerateImage:
            out[coords] = np.where(out[coords]>avg_intensity, out[coords]*0.8, out[coords]*0.1)
        elif op_type == OpType.GenerageBlackImage:
            out[coords] = np.where(out[coords]>avg_intensity, out[coords]*0.6, out[coords]*0.1)
        else:
            print('Wrong type, add s&p noise')

        return out
    elif noise_typ =="speckle":
        row,col = image.shape
        gauss = np.random.randn(row,col)
        gauss = gauss.reshape(row,col)

        if op_type == OpType.GenerateImage:
            grade = np.random.randint(1,6)
        elif op_type == OpType.GenerageBlackImage:
            grade = np.random.randint(6,20)
        else:
            print('Wrong type, add speckle noise')

        noisy = image + image * gauss * 0.01 * grade
        return noisy
