import sys
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.io import swc_writer

SWC_PATH = "../../data/optimation/gold.swc"
OUTPUT_PATH = "../../data/optimation/test4_gold.swc"


def cut_swc_rectangle(swc_tree, LFD_pos, RBT_pos):
    '''
    swc_tree: input the swc tree you want to cut
    LFD_pos: 1*3 tuple, refer to Left Front Down position of the cut rectangle
    RBT_pos: 1*3 tuple, refer to Right Behind Top position of the cut rectangle
    require:
    LFD_pos[0] < RBT_pos[0]
    LFD_pos[1] < RBT_pos[1]
    LFD_pos[2] < RBT_pos[2]
    the output region will be saved in (pyneal)/output/swc_cut/
    '''
    if LFD_pos[0] > RBT_pos[0] or LFD_pos[1] > RBT_pos[1] or LFD_pos[2] > RBT_pos[2]:
        raise Exception("[Error: ]LFD pos should be smaller than RBT pos")
    for node in swc_tree.get_node_list():
        if node.is_virtual():
            continue
        if not (LFD_pos[0] <= node.get_x() <= RBT_pos[0] and \
                LFD_pos[1] <= node.get_y() <= RBT_pos[1] and \
                LFD_pos[2] <= node.get_z() <= RBT_pos[2]):
            swc_tree.remove_node(node)
                            

if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    swc_tree = SwcTree()
    # load origin swc file
    swc_tree.load(SWC_PATH)

    cut_swc_rectangle(swc_tree, (260, 30, 125), (324, 94, 189))
    swc_tree.get_node_list(update=True)
    for node in swc_tree.get_node_list():
        node.set_x(node.get_x()-260)
        node.set_y(node.get_y()-30)
        node.set_z(node.get_z()-125)
    # the result will be saved in:
    swc_writer.swc_save(swc_tree=swc_tree, out_path=OUTPUT_PATH)
