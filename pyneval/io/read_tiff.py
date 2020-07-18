from pyneval.metric.utils.klib.TiffFile import imsave, imread, TiffFile
import os


def read_tiffs(tiff_paths):
    tiff_list = []
    if os.path.isfile(tiff_paths):
        if not (tiff_paths[-4:] == ".tif" or tiff_paths[-4:] == ".TIF"):
            print(tiff_paths + "is not a tif file")
            return None
        tiff_file = imread(tiff_paths)
        tiff_list.append(tiff_file)
    elif os.path.isdir(tiff_paths):
        for file in os.listdir(tiff_paths):
            tiff_list += read_tiffs(tiff_paths=os.path.join(tiff_paths, file))
    return tiff_list