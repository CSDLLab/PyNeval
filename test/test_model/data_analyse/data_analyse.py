import csv
from pyneval.pyneval_io import swc_io


def single_file_analyse(swc_tree):
    size = len(swc_tree.get_node_list())
    blocks = len(swc_tree.root().children)
    return size, blocks


def file_analyse(file_path):
    tree2filename = {}
    swc_trees = swc_io.read_swc_trees(file_path, tree2filename)
    info = [[],[],[]]
    for swc_tree in swc_trees:
        swc_name = tree2filename[swc_tree]
        size, blocks = single_file_analyse(swc_tree)
        info[0].append(swc_name)
        info[1].append(size)
        info[2].append(blocks)
        print("file_name = {} node num = {} blocks = {}".format(swc_name, size, blocks))
    return info


if __name__ == '__main__':
    info = file_analyse("../../../data/raw")
    with open("../../../data/raw/info.csv", 'w') as f:
        write = csv.writer(f)
        write.writerows(info)

