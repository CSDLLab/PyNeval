import os

from pyneval.errors.exceptions import InvalidTiffFileError
from pyneval.metric.utils.klib.TiffFile import TiffFile, imread, imsave


def is_tiff_file(tiff_file):
    return tiff_file[-4:] in (".tif", ".TIF")


def read_tiff(tiff_path):
    """
    Args:
        tiff_path: a tiff file path

    Returns:
        tiff image object
    """
    if not os.path.isfile(tiff_path) or not is_tiff_file(tiff_path):
        raise InvalidTiffFileError(tiff_path)
    return imread(tiff_path)


def read_tiffs(tiff_paths):
    """
    Args:
        tiff_paths: tiff_path file path for directs that contain tiff files
    Returns:
        tiff image objects
    """
    # load all tiff file paths
    tiff_files = []
    if os.path.isfile(tiff_paths):
        if not is_tiff_file(tiff_files):
            print (tiff_paths + "is not a tif file")
            return None
        tiff_files.append(tiff_paths)
    else:
        for root, _, files in os.walk(tiff_paths):
            for file in files:
                f = os.path.join(root, file)
                if is_tiff_file(f):
                    tiff_files.append(f)
    # load image objects
    tiff_list = []
    for tiff_file in tiff_files:
        tiff_list.append(imread(tiff_file))
    return tiff_list
