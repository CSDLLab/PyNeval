from pyneval.io.read_swc import read_swc_trees
from pyneval.io.save_swc import swc_save
from pyneval.model.swc_node import SwcTree
import random


def get_float_random(down, up):
    if down > up:
        return False
    res = random.random() * (up-down) + down
    return res


def build_random(swc_tree, move_percentage=None, move_num=None, move_range=1.0, tendency=(1, 1, 1)):
    '''
    :param swc_tree: standard swc tree
    :param percentage: percentage of nodes to move (range:[0,1])
    :param range:stard range is the averange length of edge.
    :param tendency: a tuple to change the direction of the movement
    :return: modified swc tree(different object from the input one)
    '''
    swc_node_list = swc_tree.get_node_list()

    # calculate which nodes to move
    node_to_move = set()
    if move_num is not None:
        while len(node_to_move) < move_num:
            move_id = random.randint(1, len(swc_node_list)-1)
            node_to_move.add(move_id)
    elif move_percentage is not None:
        tmp_num = int((len(swc_node_list)-1) * move_percentage)
        while len(node_to_move) < tmp_num:
            move_id = random.randint(1, len(swc_node_list)-1)
            node_to_move.add(move_id)

    for item in node_to_move:
        print("moved = {}".format(item))

    # calculate move base
    tot_length = 0.0
    for node in swc_node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        tot_length += node.parent_distance()
    move_base = tot_length / (len(swc_node_list) - 1)

    print("move base = {}".format(move_base))

    res_tree = swc_tree.get_copy()
    res_swc_list = res_tree.get_node_list()
    for node_id in node_to_move:
        # calculate move length
        dx, dy, dz = get_float_random(-1, 1), get_float_random(-1, 1), get_float_random(-1, 1)
        dx, dy, dz = dx * move_base, dy * move_base, dz * move_base
        dx, dy, dz = dx * tendency[0], dy * tendency[1], dz * tendency[2]

        # print("dx = {} dy = {} dz = {}".format(dx, dy, dz))
        res_swc_list[node_id].set_x(res_swc_list[node_id].get_x() + dx)
        res_swc_list[node_id].set_y(res_swc_list[node_id].get_y() + dy)
        res_swc_list[node_id].set_z(res_swc_list[node_id].get_z() + dz)

    #debug
    swc_save(res_tree, "../../output/build_out.swc")
    return res_tree


if __name__=="__main__":
    test_tree = SwcTree()
    test_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\multy_useage\push.swc")

    move_percentage = 0.2
    move_num = None
    move_range = 1.0
    move_tendency = (1, 1, 1)
    build_random(test_tree, move_percentage, move_num, move_range, move_tendency)


