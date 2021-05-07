import numpy as np

from pyneval.io import read_json
from pyneval.io.swc_writer import swc_save
from pyneval.metric.utils.klib import TiffFile
from pyneval.metric.utils.tiff_utils import front_expend_step
from pyneval.model.swc_node import SwcTree

TIFF_PATH = "../../data/optimation/6656_test.tif"


def tiff_cut(tiff_data, LDF = (0, 0, 0), len = (64, 64, 64)):
    res = tiff_data[LDF[0]:LDF[0]+len[0], LDF[1]:LDF[1]+len[1], LDF[2]:LDF[2]+len[2]]
    return res


if __name__ == "__main__":
    tiff_file = TiffFile.imread(TIFF_PATH)
    data = tiff_cut(tiff_file, LDF=(125, 30, 260))
    TiffFile.imsave("../../data/optimation/test4_test.tif", data)
    # print("??")

