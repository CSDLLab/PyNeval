import os
from pymets.model.swc_node import SwcNode,SwcTree


# if path is a fold
def read_swc_trees(swc_file_paths):
    swc_tree_list = []
    if os.path.isfile(swc_file_paths):
        if not (swc_file_paths[-4:] == ".swc" or swc_file_paths[-4:] == ".SWC"):
            print(swc_file_paths + "is not a tif file")
            return None
        swc_tree = SwcTree()
        swc_tree.load(swc_file_paths)
        swc_tree_list.append(swc_tree)
    elif os.path.isdir(swc_file_paths):
        for file in os.listdir(swc_file_paths):
            swc_tree_list += read_swc_trees(swc_file_paths=os.path.join(swc_file_paths, file))
    return swc_tree_list


def adjust_swcfile(swc_str):
    words = swc_str.split(" ")
    print(words)

if __name__ == "__main__":
    pass