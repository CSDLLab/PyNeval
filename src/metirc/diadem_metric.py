import queue
import time
import math
from src.io.read_json import read_json
from src.metirc.utils.config_utils import get_default_threshold
from src.model.binary_node import convert_to_binarytree,RIGHT
from src.model.swc_node import SwcTree,SwcNode

# 阈值
g_terminal_threshold = 0

# 开关
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

# 统计变量
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


def generate_node_weights(bin_root, spur_set):
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


def is_in_threshold(gold_node, test_node):
    pass


def get_nearby_node_list(gold_node=None, bin_test_set=None, check_previous_use=False):
    nearby_node_list = []

    for test_node in bin_test_set:
        if (not check_previous_use or test_node not in g_matches) and is_in_threshold(gold_node, test_node):
            nearby_node_list.append(test_node)

    return nearby_node_list

def get_end_node_XY_dis_diff(gold_swc_node,
                             trajectory,
                             test_swc_node):
    gold_dist = gold_swc_node.distance(trajectory,mode=_2D)
    test_dist = test_swc_node.distance(trajectory,mode=_2D)
    return gold_dist - test_dist

def get_end_node_Z_dis_diff(gold_swc_node,
                            trajectory,
                            test_swc_node):
    gold_dist = math.fabs(gold_swc_node.z - trajectory.z)
    test_dist = math.fabs(test_swc_node.z - trajectory.z)
    return gold_dist - test_dist


def get_closest_match(gold_node,
                      bin_gold_list,
                      bin_test_list,
                      DEBUG = False):
    best_match = None

    # Step1: 寻找阈值内的节点
    nearby_list = get_nearby_list(gold_node, bin_test_list)
    if DEBUG:
        print("nearby list of {}:".format(gold_node.to_str))
        for node in nearby_list:
            print(node.to_str())

    # Step2: 寻找到上下节点匹配的点，标记为match
    match_list = []
    for nearby_node in nearby_list:
        if is_diadem_match(gold_node, nearby_node, bin_gold_list, bin_test_list):
            match_list.append(nearby_node)

    if len(match_list) == 1:
        best_match = match_list[0]
    elif len(match_list) >= 1:
        best_match = get_best_match(match_list, gold_node, bin_test_list)

    return best_match


def is_continuation(gold_node, bin_test_list, add_to_list=True, DEBUG = False):
    if not gold_node.has_children():
        return False

    ancestor_node_matches = []
    gold_path_length = SwcNode()

    # 寻找gold_node第一个匹配的祖先
    ancestor_match = None
    ancestor_gold = gold_node.parent()
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

    # 寻找失败
    return False


def weight_excess(bin_test_root, goldtree):

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

    # 根节点肯定匹配
    g_matches[bin_gold_root] = bin_test_root
    g_matches[bin_test_root] = bin_gold_root

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

            # 补偿一种寻找方式 (暂时省略)
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

    t_remove = []
    for miss_node in g_miss:
        miss_data = miss_node.data
        if not miss_data.is_leaf():
            if is_continuation(miss_node, bin_test_list):
                weight = g_weight_dict[miss_node]
                g_score_sum += weight
                if DEBUG:
                    print("[Info: ] find continuation in miss nodes {}".format(miss_node.to_str()))
                t_remove.append(miss_node)

    for node in t_remove:
        g_miss.remove(node)

    if g_weight_sum > 0:
        g_direct_match_score = g_quantity_score_sum / number_of_nodes
        g_quantity_score = g_score_sum / g_weight_sum

        if g_remove_spur > 0:
            remove_spurs(bin_test_root)

        if g_count_excess_nodes:
            g_weight_sum += weight_excess(bin_test_root, goldtree)

        g_final_score = g_score_sum / g_weight_sum


def diadem_metric(swc_gold_tree, swc_test_tree, config):
    global g_spur_set
    global g_weight_dict

    if g_align_tree_by_root:
        swc_test_tree.align_root(swc_gold_tree)

    bin_gold_root = convert_to_binarytree(swc_gold_tree)
    bin_test_root = convert_to_binarytree(swc_test_tree)
    print(bin_gold_root.data.id())
    if g_remove_spur > 0:
        g_spur_set = remove_spurs(bin_gold_root,1.0)

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
    # print(length_metric(test_swc_tree=testTree, gold_swc_tree=goldtree,config=read_json("D:\gitProject\mine\PyMets\\test\length_metric.json")))
    print(diadem_metric(swc_test_tree=testTree,
                        swc_gold_tree=goldtree,
                        config=read_json("D:\gitProject\mine\PyMets\\test\length_metric.json")))
    # print(length_metric(test_swc_tree=testTree, gold_swc_tree=goldtree,config=read_json("D:\gitProject\mine\PyMets\\test\length_metric.json")))

    print(time.time() - start)