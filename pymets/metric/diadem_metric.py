import queue
import time
import math
from pymets.io.read_json import read_json
from pymets.metric.utils.config_utils import get_default_threshold
from pymets.model.binary_node import BinaryNode,RIGHT
from pymets.model.swc_node import SwcTree, SwcNode
from pymets.model.euclidean_point import EuclideanPoint
from pymets.metric.utils.diadam_match_utils import \
    get_match_path_length_difference, get_nearby_node_list, \
    get_end_node_XY_dis_diff, get_end_node_Z_dis_diff, get_trajectory_for_path, \
    path_length_matches
from pymets.metric.utils.bin_utils import convert_to_binarytree

# thresholds
g_terminal_threshold = 0

# switch
g_remove_spur = False
g_align_tree_by_root = False
g_count_excess_nodes = True

WEIGHT_MODE = 1
WEIGHT_DEGREE = 1
WEIGHT_SQRT_DEGREE = 2
WEIGHT_DEGREE_HARMONIC_MEAN = 3
WEIGHT_PATH_LENGTH = 4
WEIGHT_UNIFORM = 5
_2D = '2d'
_3D = '3d'

# various
g_weight_sum = 0
g_score_sum = 0
g_quantity_score_sum = 0
g_quantity_score = 0
g_direct_match_score = 0
g_final_score = -1

g_miss = set()
g_spur_set = set()
g_matches = {}
g_weight_dict = {}
g_excess_nodes = {}


def remove_spurs(bin_root, threshold):
    spur_set = set()
    both_children_spur = False

    stack = queue.LifoQueue()

    if bin_root.has_children:
        stack.put(bin_root)

    while not stack.empty():
        node = stack.get()
        if node.has_children():
            stack.put(node.left_son)
            stack.put(node.right_son)
        else:
            distance = node.data.path_length
            if distance < threshold and not (node in g_matches):
                both_children_spur = False
                spur_set.add(node)
                if node.get_side() == RIGHT:
                    l_node = node.parent.left_son
                    if not l_node.has_children and \
                            l_node.data.path_length < threshold and \
                            not l_node in g_matches:
                        both_children_spur = True
                        spur_set.add(l_node)
                        ll_node = stack.get()
                        if ll_node != l_node:
                            raise Exception("[Error:  ] stack top is not current node's twin")

                if not both_children_spur:
                    spur_set.add(node.parent)
    return spur_set


def generate_node_weights(bin_root, spur_set, DEBUG=False):
    init_stack = queue.LifoQueue()
    main_stack = queue.LifoQueue()
    degree_dict = {}
    global g_weight_dict
    degree = 0

    init_stack.put(bin_root)
    main_stack.put(bin_root)

    while not init_stack.empty():
        node = init_stack.get()
        if node.has_children():
            init_stack.put(node.left_son)
            init_stack.put(node.right_son)
            main_stack.put(node.left_son)
            main_stack.put(node.right_son)

    while not main_stack.empty():
        node = main_stack.get()

        if WEIGHT_MODE == WEIGHT_UNIFORM:
            g_weight_dict[node] = 1
        else:
            if DEBUG:
                print("Determining weight for {}".format(node.data.id))

            if node.is_leaf():
                g_weight_dict[node] = 1
                degree_dict[node] = 1
            else:
                degree = 0
                if node.left_son.is_leaf() and node.right_son.is_leaf():
                    if node.left_son in spur_set or node.right_son in spur_set:
                        degree = 1
                    else:
                        degree = 2
                elif node in spur_set:
                    if node.left_son.is_leaf():
                        degree += degree_dict[node.right_son]
                    else:
                        degree += degree_dict[node.left_son]
                else:
                    degree += degree_dict[node.left_son]
                    degree += degree_dict[node.right_son]
                degree_dict[node] = degree
                if WEIGHT_MODE == WEIGHT_DEGREE:
                    g_weight_dict[node] = degree
                elif WEIGHT_MODE == WEIGHT_SQRT_DEGREE:
                    g_weight_dict[node] = math.sqrt(degree)
                elif WEIGHT_MODE == WEIGHT_DEGREE_HARMONIC_MEAN:
                    g_weight_dict[node] = 2.0 / (1.0/degree_dict[node.getLeft()] + 1.0/degree_dict.get[node.getRight()])
                elif WEIGHT_MODE == WEIGHT_PATH_LENGTH:
                    g_weight_dict[node] = node.data.path_length
                if DEBUG:
                    print("nodeId = {}, degree = {}".format(node.data._id, degree))
                    if node.parent is not None:
                        print("pa = {}".format(node.parent.data._id))
                    print("-----------")


def is_diadem_match(gold_node, nearby_node, bin_gold_list, bin_test_list, DEBUG=False):
    if gold_node.data.get_id() == 1320 and nearby_node.data.get_id() == 1269:
        print("??")
    length_diff = get_match_path_length_difference(gold_node, nearby_node, bin_gold_list, bin_test_list)
    if DEBUG:
        print("gold_node = {}, test_node = {}, length_diff = {}".format(
            gold_node.data.get_id(), nearby_node.data.get_id(), length_diff
        ))
    if length_diff < 1:
        return True
    else:
        return False


def get_best_match(match_list, gold_node, bin_test_list,DEBUG=False):
    if DEBUG:
        print("Determining best match")
    confirm_list = []

    gold_data = gold_node.data
    des_branch_left = {}
    trajactory_map = {}

    if gold_node.has_children():
        nearby_list = []
        path_length_map = {}
        path_length_map[gold_node] = SwcNode()

        target_dis_list = []
        for test_node in match_list:
            target_distances = SwcNode()
            target_distances.xy_path_length = gold_node.data.distance(test_node.data, _2D)
            target_distances.z_path_length = gold_node.data.distance(test_node.data, _2D)
            target_dis_list.append(target_distances)

        current_list = []
        current_list.append(gold_node.left_son)
        trajactory_map[gold_node.left_son] = gold_node.data.left_trajectory
        des_branch_left[gold_node.left_son] = True

        current_list.append(gold_node.right_son)
        trajactory_map[gold_node.right_son] = gold_node.data.right_trajectory
        des_branch_left[gold_node.right_son] = False

        target_tra = EuclideanPoint
        while len(current_list) > 0 and len(confirm_list) == 0:
            next_list = []
            for des_node in current_list:
                target_tra = trajactory_map[des_node]

                if target_tra.get_x() == -1.0 or target_tra.get_z() == -1.0:
                    tmp_tra = get_trajectory_for_path(gold_node, des_node)
                    if target_tra.get_x() == -1.0:
                        target_tra.set_x(tmp_tra.get_x())
                        target_tra.set_y(tmp_tra.get_y())
                    if target_tra.get_z() == -1.0:
                        target_tra.set_z(tmp_tra.get_z())
                des_tra = des_node.data.parent_trajectory

                if des_node.has_children():
                    next_list.append(des_node.left_son)
                    next_list.append(des_node.right_son)
                    trajactory_map[des_node.left_son] = target_tra
                    trajactory_map[des_node.right_son] = target_tra

                gold_path_length = SwcNode()
                gold_path_length.add_length(des_node.data)
                parent_path_length = path_length_map[des_node.parent]
                gold_path_length.add_length(parent_path_length)
                path_length_map[des_node] = gold_path_length

                nearby_list = get_nearby_node_list(des_node, bin_test_list, check_previous_use=True)

                for test_node in nearby_list:
                    test_des_node = test_node
                    test_path_length = SwcNode()

                    des_dis = SwcNode()
                    des_dis.xy_path_length = des_node.data.distance(test_node.data, _2D)
                    des_dis.z_path_length = math.fabs(des_node.data.get_z() - test_node.data.get_z())

                    while test_node.parent is not None:
                        test_path_length.add_length(test_node.data)
                        test_node = test_node.parent
                        tmp_list = []
                        for match in match_list:
                            if test_node == match:
                                test_XY_path_length = test_path_length.xy_path_length + \
                                                      get_end_node_XY_dis_diff(gold_data, target_tra, test_node.data) + \
                                                      get_end_node_XY_dis_diff(des_node.data, des_tra, test_des_node.data)
                                test_Z_path_length = test_path_length.z_path_length + \
                                                     get_end_node_Z_dis_diff(gold_data, target_tra, test_node.data) + \
                                                     get_end_node_Z_dis_diff(des_node.data, des_tra, test_des_node.data)

                                if path_length_matches(gold_path_length, test_XY_path_length, test_Z_path_length) < 1:
                                    confirm_list.append(match)
                                    tmp_list.append(match)

                        for node in tmp_list:
                            match_list.remove(node)
                        while len(tmp_list):
                            tmp_list.pop()

            current_list = nearby_list
    if len(confirm_list) == 1:
        return confirm_list[0]

    if len(confirm_list) == 0:
        confirm_list = match_list

    dis = 0
    closest_dis = -1
    closest_match = None
    for test_node in confirm_list:
        dis = test_node.data.distance(gold_node.data)
        if closest_dis == -1 or dis < closest_dis:
            closest_dis = dis
            closest_match = test_node

    return closest_match


def get_closest_match(gold_node,
                      bin_gold_list,
                      bin_test_list,
                      DEBUG=False):
    best_match = None

    # Step1: find node within threshold
    nearby_list = get_nearby_node_list(gold_node=gold_node, bin_test_list=bin_test_list,
                                       g_matches=g_matches)
    if DEBUG:
        print("nearby list of {}:".format(gold_node.data.get_id()))
        for node in nearby_list:
            print(node.data.get_id())
        print("----END----")

    # Step2: find match node whose ancestor is also matched
    match_list = []
    for nearby_node in nearby_list:
        if is_diadem_match(gold_node, nearby_node, bin_gold_list, bin_test_list):
            if DEBUG:
                print("{} {}".format(
                    gold_node.data.get_id(), nearby_node.data.get_id()
                ))
            match_list.append(nearby_node)

    if len(match_list) == 1:
        best_match = match_list[0]
    elif len(match_list) >= 1:
        best_match = get_best_match(match_list, gold_node, bin_test_list)

    if best_match is not None:
        print("best match {} {}".format(gold_node.data.get_id(), best_match.data.get_id()))
    else:
        print("best match {} None".format(gold_node.data.get_id()))
    return best_match


def is_continuation(gold_node, bin_test_list, add_to_list=True, DEBUG = False):
    if not gold_node.has_children():
        return False

    ancestor_node_matches = []
    gold_path_length = SwcNode()

    # find the first matched ancestor of the gold_node
    ancestor_match = None
    ancestor_gold = gold_node.parent
    gold_path_length.path_length = gold_node.data.path_length
    gold_path_length.xy_path_length = gold_node.data.xy_path_length
    gold_path_length.z_path_length = gold_node.data.z_path_length
    is_match = False
    ancestor_match = False
    is_left = False

    if DEBUG:
        print("gold_path_length: path_length {}, xy_path_length {}, z_path_length {}".format(
            gold_path_length.path_length,
            gold_path_length.xy_path_length,
            gold_path_length.z_path_length
        ))
    while ancestor_gold is not None and not ancestor_match:
        if ancestor_gold in g_matches.keys():
            ancestor_match = g_matches[ancestor_gold]
            if is_sub_continuation(gold_node, ancestor_gold, ancestor_match,is_left,
                                   gold_path_length, bin_test_list, add_to_list):
                return True
            ancestor_match = True
        ancester_nearby_list = get_nearby_node_list(ancestor_gold, bin_test_list)
        for a_n_node in ancester_nearby_list:
            if is_sub_continuation(gold_node, ancestor_gold, ancestor_match,is_left,
                                   gold_path_length, bin_test_list, add_to_list):
                return True
        gold_path_length.path_length += ancestor_gold.data.path_length
        gold_path_length.xy_path_length += ancestor_gold.data.xy_path_length
        gold_path_length.z_path_length += ancestor_gold.data. z_path_length
        is_left = ancestor_gold.is_left()
        ancestor_gold = ancestor_gold.parent

    # failed
    return False


def weight_excess(bin_test_root, gold_tree):
    global g_excess_nodes

    sum_weight = 0.0
    gold_bin_list = goldtree.get_node_list()

    setup_stack = queue.LifoQueue()
    use_stack = queue.LifoQueue()

    setup_stack.put(bin_test_root)
    while not setup_stack.empty():
        node = setup_stack.get()
        if node.has_children():
            setup_stack.put(node.left_son)
            setup_stack.put(node.right_son)
            use_stack.put(node.left_son)
            use_stack.put(node.right_son)

    direct_term_excess = {}

    while not use_stack.empty():
        node = use_stack.get()
        data = node.data

        if node.has_children():
            num_excess_node = direct_term_excess[node.left_son]
            num_excess_node += direct_term_excess[node.right_son]
            excess_weight = get_excess_weight(num_excess_node, node, direct_term_excess)

            if not node in g_matches.keys() and \
                    len(get_nearby_node_list(node, gold_bin_list)) == 0 and \
                    not is_continuation(node, gold_bin_list, add_to_list=False):
                g_excess_nodes[node] = excess_weight
                if not node in g_spur_set:
                    sum_weight += excess_weight
            else:
                num_excess_node = 0
                excess_weight = 0
        else:
            num_excess_node = 0
            excess_weight = 0

            if not node in g_spur_set and node not in g_matches.keys() and node.parent not in g_matches.keys():
                nearby_nodes = get_nearby_node_list(node, gold_bin_list)
                if len(nearby_nodes) == 0:
                    remove_nearest_node(node, nearby_nodes, gold_bin_list)
                else:
                    num_excess_node = 1
                    excess_weight = 1
                    g_excess_nodes[node] = 1
                    sum_weight += excess_weight

        direct_term_excess[node] = num_excess_node
    return sum_weight



def score_trees(bin_gold_root, bin_test_root,DEBUG=False):
    global g_weight_dict
    global g_weight_sum
    global g_score_sum
    global g_quantity_score_sum
    global g_final_score

    stack = queue.LifoQueue()
    number_of_nodes = 0
    weight = 0

    bin_gold_list = bin_gold_root.get_node_list()
    bin_test_list = bin_test_root.get_node_list()

    # Root is certainly matched
    # g_matches[bin_gold_root] = bin_test_root
    # g_matches[bin_test_root] = bin_gold_root

    number_of_nodes -= len(g_spur_set)
    number_of_nodes += len(bin_gold_list)
    stack.put(bin_gold_root)

    while not stack.empty():
        gold_node = stack.get()
        gold_data = gold_node.data

        if gold_node.has_children():
            stack.put(gold_node.left_son)
            stack.put(gold_node.right_son)

        if gold_node in g_spur_set:
            pass
        else:
            weight = g_weight_dict[gold_node]
            g_weight_sum += weight

            if DEBUG:
                print(gold_node.to_str())

            match = get_closest_match(gold_node = gold_node,
                                      bin_gold_list = bin_gold_list,
                                      bin_test_list = bin_test_list)

            # another match method (temporarily undo)
            # if match is None and gold_node.is_leaf() and g_terminal_threshold > 0:
            #     match = get_extended_termination_match(gold_node = gold_node,
            #                                            bin_gold_list = bin_gold_list,
            #                                            bin_test_list = bin_test_list)

            if match is not None:
                g_matches[gold_node] = match
                g_matches[match] = gold_node
                g_score_sum += weight

                # Increment quantity (non-continuations)
                g_quantity_score_sum += 1
            else:
                g_miss.add(gold_node)

    # t_remove = []
    # for miss_node in g_miss:
    #     miss_data = miss_node.data
    #     if miss_node.left_son is not None or miss_node.right_son is not None:
    #         if is_continuation(miss_node, bin_test_list):
    #             weight = g_weight_dict[miss_node]
    #             g_score_sum += weight
    #             if DEBUG:
    #                 print("[Info: ] find continuation in miss nodes {}".format(miss_node.to_str()))
    #             t_remove.append(miss_node)
    #
    # for node in t_remove:
    #     g_miss.remove(node)
    #
    # if g_weight_sum > 0:
    #     g_direct_match_score = g_quantity_score_sum / number_of_nodes
    #     g_quantity_score = g_score_sum / g_weight_sum
    #
    #     if g_remove_spur > 0:
    #         remove_spurs(bin_test_root)
    #
    #     if g_count_excess_nodes:
    #         # g_weight_sum += weight_excess(bin_test_root, goldtree)
    #         pass
    #
    #     g_final_score = g_score_sum / g_weight_sum


def diadem_metric(swc_gold_tree, swc_test_tree, config):
    global g_spur_set
    global g_weight_dict

    if g_align_tree_by_root:
        swc_test_tree.align_root(swc_gold_tree)

    bin_gold_root = convert_to_binarytree(swc_gold_tree)
    bin_test_root = convert_to_binarytree(swc_test_tree)

    if g_remove_spur > 0:
        g_spur_set = remove_spurs(bin_gold_root, 1.0)

    generate_node_weights(bin_gold_root, g_spur_set)
    score_trees(bin_gold_root, bin_test_root, DEBUG=False)
    return 0


if __name__ == "__main__":
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\ExampleGoldStandard.swc")
    get_default_threshold(goldtree)

    testTree = SwcTree()
    testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\ExampleTest.swc")

    start = time.time()
    print(diadem_metric(swc_test_tree=testTree,
                        swc_gold_tree=goldtree,
                        config=read_json("D:\gitProject\mine\PyMets\config\diadem_metric.json")))

    print(time.time() - start)