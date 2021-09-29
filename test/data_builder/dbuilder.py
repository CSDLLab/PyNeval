import os

from pyneval.pyneval_io import swc_io
import random


def get_float_random(down, up):
    if down > up:
        return False
    res = random.random() * (up-down) + down
    return res


def swc_random_delete(swc_tree, move_percentage=None, move_num=None):
    '''
    :param move_percentage:
    :param swc_tree:
    :return: randomly remove a node from the original tree
    '''

    swc_node_list = swc_tree.get_node_list()

    # calculate which nodes to move_5
    node_to_move = [i for i in range(1, len(swc_node_list))]
    if move_num is not None:
        node_to_move = node_to_move[:move_num]
    elif move_percentage is not None:
        node_to_move = node_to_move[:int(move_percentage*len(swc_node_list))]
    else:
        return False

    res_tree = swc_tree.get_copy()
    swc_node_list = res_tree.get_node_list()

    for remove_id in node_to_move:
        remove_node = swc_node_list[remove_id]
        # for son in remove_node.children:
        #     son.parent = res_tree.root()
        res_tree.remove_node(remove_node.parent, remove_node)
        # remove_node.parent.remove_child(remove_node)
        remove_node.parent = None
    res_tree.get_node_list(update=True)
    # swc_save(res_tree, "D:\gitProject\mine\PyNeval\output\\build_out.swc")
    return res_tree


def swc_random_move(swc_tree, move_percentage=None, move_num=None, move_range=1.0, tendency=(1, 1, 1)):
    '''
    :param swc_tree: standard swc tree
    :param percentage: percentage of nodes to move (range:[0,1])
    :param range:stard range is the averange length of edge.
    :param tendency: a tuple to change the direction of the movement
    :return: modified swc tree(different object from the input one)
    '''
    swc_node_list = swc_tree.get_node_list()

    # calculate move_5 base
    tot_rad = 0.0
    for node in swc_node_list:
        if node.is_virtual():
            continue
        tot_rad += node.radius()
    move_base = tot_rad / float(len(swc_node_list) - 1) * move_range

    # calculate which nodes to volume_move
    node_to_move = [i for i in range(1, len(swc_node_list))]
    random.shuffle(node_to_move)
    if move_num is not None:
        node_to_move = node_to_move[:move_num]
    elif move_percentage is not None:
        node_to_move = node_to_move[:int(move_percentage*len(swc_node_list))]
    else:
        return False

    res_tree = swc_tree.get_copy()
    res_swc_list = res_tree.get_node_list()
    for node_id in node_to_move:
        # calculate move_5 length
        dx, dy, dz = get_float_random(-1, 1), get_float_random(-1, 1), get_float_random(-1, 1)
        dx, dy, dz = dx * move_base, dy * move_base, dz * move_base
        dx, dy, dz = dx * tendency[0], dy * tendency[1], dz * tendency[2]

        # print("dx = {} dy = {} dz = {}".format(dx, dy, dz))
        res_swc_list[node_id].set_x(res_swc_list[node_id].get_x() + dx)
        res_swc_list[node_id].set_y(res_swc_list[node_id].get_y() + dy)
        res_swc_list[node_id].set_z(res_swc_list[node_id].get_z() + dz)

    # debug
    # swc_save(res_tree, "D:\gitProject\mine\PyNeval\output\\build_out.swc")
    return res_tree


def swc_random_link(swc_tree, move_percentage=None, move_num=None):
    '''
    :param swc_tree: standard swc tree
    :param percentage: percentage of nodes to volume_move (range:[0,1])
    :param range:stard range is the averange length of edge.
    :param tendency: a tuple to change the direction of the movement
    :return: modified swc tree(different object from the input one)
    '''
    branch_list = swc_tree.get_branch_swc_list()

    # calculate which nodes to volume_move
    node_to_modify = [i for i in range(1, len(branch_list))]
    random.shuffle(node_to_modify)
    if move_num is not None:
        node_to_modify = node_to_modify[:move_num]
    elif move_percentage is not None:
        node_to_modify = node_to_modify[:int(move_percentage*len(branch_list))]
    else:
        return False

    res_tree = swc_tree.get_copy()
    res_swc_list = res_tree.get_branch_swc_list()

    for node_id in node_to_modify:
        pa = res_swc_list[node_id]
        rm_c_id = -1
        if len(res_swc_list[node_id].children) >= 1:
            rm_c_id = random.randint(0, len(res_swc_list[node_id].children) - 1)
        if rm_c_id == -1:
            continue
        son = res_swc_list[node_id].children[rm_c_id]

        res_tree.unlink_child(son)

        res_tree.link_child(pa.parent, son)
    return res_tree


def generate_data():
    tree_name_dict = {}
    gold_trees = swc_io.read_swc_trees(swc_file_paths="../../data/example_selected",
                                       tree_name_dict=tree_name_dict)
    iter_num = 10
    move_num = None
    move_range = 2.0
    move_tendency = (1, 1, 1)
    output_dir = "../../output/random_data"
    # decide the origin swc tree
    for gold_tree in gold_trees:
        # decide how much modes to change
        tree_name = tree_name_dict[gold_tree]
        tree_dir = os.path.join(output_dir, tree_name[:-4])
        if not os.path.exists(tree_dir):
            os.mkdir(tree_dir)
        for move_percentage in range(1, 11):
            # take random for gen_num times
            percent_dir = os.path.join(tree_dir, "{:03d}".format(move_percentage*10))
            if not os.path.exists(percent_dir):
                os.mkdir(percent_dir)
            for it in range(iter_num):
                test_swc = swc_random_move(swc_tree=gold_tree,
                                           move_percentage=0.1 * move_percentage,
                                           move_num=None,
                                           move_range=move_range,
                                           tendency=move_tendency)
                # test_swc = swc_random_delete(swc_tree=gold_tree,
                #                              move_percentage=0.1*move_percentage,
                #                              move_num=None)
                # test_swc = swc_random_link(swc_tree=gold_tree,
                #                            move_percentage=0.1 * move_percentage,
                #                            move_num=None)
                file_name = os.path.join(percent_dir, "move_{:02d}.swc".format(it))
                swc_io.swc_save(swc_tree=test_swc, out_path=file_name)


if __name__ == "__main__":
    generate_data()
