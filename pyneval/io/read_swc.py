import os

from pyneval.errors.exceptions import InvalidSwcFileError
from pyneval.model.swc_node import SwcNode, SwcTree


def is_swc_file(file_path):
    return file_path[-4:] in (".swc", ".SWC")

def read_swc_tree(swc_file_path):
    if not os.path.isfile(swc_file_path) or not is_swc_file(swc_file_path):
        raise InvalidSwcFileError(swc_file_path)
    swc_tree = SwcTree()
    swc_tree.load(swc_file_path)
    return swc_tree

# if path is a folder
def read_swc_trees(swc_file_paths, tree_name_dict=None):
    """
    Read a swc tree or recursively read all the swc trees in a fold
    Args:
        swc_file_paths(string): path to read swc
        tree_name_dict(dict): a map for swc tree and its file name
            key(SwcTree): SwcTree object
            value(string): name of the swc tree
    Output:
        swc_tree_list(list): a list shaped 1*n, containing all the swc tree in the path
    """
    # get all swc files
    swc_files = []
    if os.path.isfile(swc_file_paths):
        if not is_swc_file(swc_file_paths):
            print(swc_file_paths + "is not a swc file")
            return
        swc_files = [swc_file_paths]
    else:
        for root, _, files in os.walk(swc_file_paths):
            for file in files:
                f = os.path.join(root, file)
                if is_swc_file(f):
                    swc_files.append(f)
    # load swc trees
    swc_tree_list = []
    for swc_file in swc_files:
        swc_tree = SwcTree()
        swc_tree.load(swc_file)
        swc_tree_list.append(swc_tree)
        if tree_name_dict is not None:
            tree_name_dict[swc_tree] = os.path.basename(swc_file)
    return swc_tree_list


def adjust_swcfile(swc_str):
    words = swc_str.split("\n")
    return words


def read_from_str(swc_str):
    swc_tree = SwcTree()
    swc_list = adjust_swcfile(swc_str)
    swc_tree.load_list(swc_list)
    return swc_tree


if __name__ == "__main__":
    tree = SwcTree()
    tree.load()
    pass
