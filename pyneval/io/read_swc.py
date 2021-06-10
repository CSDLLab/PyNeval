import os
from pyneval.model.swc_node import SwcNode, SwcTree


# if path is a fold
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
    swc_tree_list = []
    if os.path.isfile(swc_file_paths):
        if not (swc_file_paths[-4:] == ".swc" or swc_file_paths[-4:] == ".SWC"):
            print(swc_file_paths + "is not a swc file")
            return None
        swc_tree = SwcTree()
        swc_tree.load(swc_file_paths)
        swc_tree_list.append(swc_tree)
        if tree_name_dict is not None:
            tree_name_dict[swc_tree] = os.path.basename(swc_file_paths)
    elif os.path.isdir(swc_file_paths):
        for file in os.listdir(swc_file_paths):
            swc_tree = read_swc_trees(swc_file_paths=os.path.join(swc_file_paths, file), tree_name_dict=tree_name_dict)
            if swc_tree is not None:
                swc_tree_list += swc_tree
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
