import numpy as np

from pyneval.pyneval_io import json_io
from pyneval.pyneval_io.swc_io import swc_save
from pyneval.metric.utils.klib import TiffFile
from pyneval.metric.utils.tiff_utils import front_expend_step
from pyneval.model.swc_tree import SwcTree

TIFF_PATH = "../../data/optimation/6656_test.tif"


def tiff_cut(tiff_data, LDF = (0, 0, 0), len = (64, 64, 64)):
    res = tiff_data[LDF[0]:LDF[0]+len[0], LDF[1]:LDF[1]+len[1], LDF[2]:LDF[2]+len[2]]
    return res
