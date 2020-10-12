import copy
import sys
import numpy as np
from pyneval.metric.utils.config_utils import DINF
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.km_utils import KM
from pyneval.io.read_json import read_json


def debug_out_list(swc_list, _str):
    print("[debug_out_list ]" + _str + str(len(swc_list)))
    # for node in swc_list:
    #     print(node.get_id())


def get_branch_swc_list(swc_tree):
    swc_list = swc_tree.get_node_list()
    branch_list = []
    for node in swc_list:
        if node.is_virtual():
            continue
        if node.parent.is_virtual():
            if len(node.children) > 2:
                branch_list.append(node)
        elif len(node.children) > 1:
            branch_list.append(node)
    return branch_list


def get_leaf_swc_list(swc_tree):
    swc_list = swc_tree.get_node_list()
    leaf_list = []
    for node in swc_list:
        if node.is_virtual():
            continue
        if len(node.children) == 0:
            leaf_list.append(node)
    return leaf_list


def get_simple_lca_length(std_tree, id_tree_dict, node1, node2):
    if std_tree.depth_array is None:
        raise Exception("[Error: ] std has not been lca initialized yet")

    tmp_node1 = id_tree_dict[node1.get_center_as_tuple()]
    tmp_node2 = id_tree_dict[node2.get_center_as_tuple()]

    lca_id = std_tree.get_lca(tmp_node1.get_id(), tmp_node2.get_id())
    if lca_id == -1:
        return DINF

    lca_node = id_tree_dict[lca_id]
    return tmp_node1.root_length + tmp_node2.root_length - 2*lca_node.root_length


def get_dis_graph(gold_tree, test_tree, test_node_list, gold_node_list, threshold_dis, mode=1):
    """
    We use KM algorithm to get the minimum full match between gold and test branch&leaf nodes
    Since KM is used for calculating maximum match, we use the opposite value of distance
    mode = 1: distance between nodes are calculated as euclidean distance
    mode = 2: distance between nodes are calculated as distance on the gold tree
    """
    std_tree = gold_tree.get_copy()
    id_tree_dict = {}

    if mode == 2:
        std_tree.get_lca_preprocess()
        for node in std_tree.get_node_list():
            # same id in gold_tree and test_tree may refer to different nodes
            id_tree_dict[node.get_center_as_tuple()] = node
            id_tree_dict[node.get_id()] = node

    # KM works only when the length of the first dimensionality is SMALLER than the second one
    # so we need to switch gold and test when gold list is SMALLER
    switch = False
    test_len = len(test_node_list)
    gold_len = len(gold_node_list)

    if gold_len < test_len:
        switch = True
        test_len, gold_len = gold_len, test_len
        test_node_list, gold_node_list = gold_node_list, test_node_list
        gold_tree, test_tree = test_tree, gold_tree

    dis_graph = np.zeros(shape=(test_len, gold_len))

    for i in range(test_len):
        for j in range(gold_len):
            if mode == 1:
                dis = test_node_list[i].distance(gold_node_list[j])
            else:
                dis = get_simple_lca_length(std_tree=std_tree,
                                            id_tree_dict=id_tree_dict,
                                            node1=test_node_list[i],
                                            node2=gold_node_list[j])

            if dis < threshold_dis:
                dis_graph[i][j] = -dis
            else:
                dis_graph[i][j] = -0x3f3f3f3f/2

    dis_graph = dis_graph.tolist()
    return dis_graph, switch, test_len, gold_len


def get_result(test_len, gold_len, switch, km, threshold_dis):
    false_pos_num, true_neg_num, true_pos_num = 0, 0, 0
    # count numer of nodes which are matched, calculate FP, TN, TP
    for i in range(0, gold_len):
        if km.match[i] != -1 and km.G[km.match[i]][i] != -0x3f3f3f3f / 2:
            true_pos_num += 1
    false_pos_num = gold_len - true_pos_num
    true_neg_num = test_len - true_pos_num

    # definition of swich is in function "get_dis_graph"
    if switch:
        true_neg_num, false_pos_num = false_pos_num, true_neg_num

    if true_pos_num != 0:
        mean_dis = -km.get_max_dis() / true_pos_num
    else:
        mean_dis = 0.0
    if mean_dis == -0.0:
        mean_dis = 0.0

    pt_cost = -km.get_max_dis() + threshold_dis * (false_pos_num + true_neg_num) / (
                false_pos_num + true_neg_num + true_pos_num)

    # debug:
    # print("output")
    # print(false_pos_num)
    # print(true_neg_num)
    # print(mean_dis)
    # print(pt_cost)
    return false_pos_num, true_neg_num, mean_dis, pt_cost


def score_point_distance(gold_tree, test_tree, test_node_list, gold_node_list, threshold_dis, mode):
    # disgraph is a 2D ndarray store the distance of nodes in gold and test
    # test_node_list contains only branch or leaf nodes
    dis_graph, switch, test_len, gold_len = get_dis_graph(gold_tree=gold_tree,
                                                          test_tree=test_tree,
                                                          test_node_list=test_node_list,
                                                          gold_node_list=gold_node_list,
                                                          threshold_dis=threshold_dis,
                                                          mode=mode)

    km = KM(maxn=max(test_len, gold_len)+10, nx=test_len, ny=gold_len, G=dis_graph)
    km.solve()

    false_pos_num, true_neg_num, mean_dis, pt_cost = get_result(test_len=test_len,
                                                                gold_len=gold_len,
                                                                switch=switch,
                                                                km=km,
                                                                threshold_dis=threshold_dis)
    return false_pos_num, true_neg_num, mean_dis, pt_cost


def branch_leaf_metric(test_swc_tree, gold_swc_tree, config):
    threshold_dis = config["threshold_dis"]
    mode = config["mode"]
    test_branch_swc_list = get_branch_swc_list(test_swc_tree)
    gold_branch_swc_list = get_branch_swc_list(gold_swc_tree)
    test_leaf_swc_list = get_leaf_swc_list(test_swc_tree)
    gold_leaf_swc_list = get_leaf_swc_list(gold_swc_tree)

    # debug output
    # debug_out_list(test_branch_swc_list, "test_branch_swc_list")
    # debug_out_list(gold_branch_swc_list, "gold_branch_swc_list")
    # debug_out_list(test_leaf_swc_list, "test_leaf_swc_list")
    # debug_out_list(gold_leaf_swc_list, "gold_leaf_swc_list")

    # result[0]:false_pos_num
    # result[1]:true_neg_num
    # result[2]:mean_dis
    # result[3]:pt_cost
    leaf_result = score_point_distance(gold_tree=gold_swc_tree,
                                       test_tree=test_swc_tree,
                                       test_node_list=test_leaf_swc_list,
                                       gold_node_list=gold_leaf_swc_list,
                                       threshold_dis=threshold_dis,
                                       mode=mode)
    branch_result = score_point_distance(gold_tree=gold_swc_tree,
                                         test_tree=test_swc_tree,
                                         test_node_list=test_branch_swc_list,
                                         gold_node_list=gold_branch_swc_list,
                                         threshold_dis=threshold_dis,
                                         mode=mode)

    return branch_result, leaf_result


if __name__ == "__main__":
    gold_swc_tree = SwcTree()
    test_swc_tree = SwcTree()
    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\branch_metric\\branch4.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\branch_metric\\branch4.swc")
    test_swc_tree.load("..\\..\\data\\branch_metric_data\\test\\1_6_Ch2_1.swc")
    gold_swc_tree.load("..\\..\\data\\branch_metric_data\\gold\\1_6_Ch2_1.swc")
    config = read_json("..\\..\\config\\branch_metric.json")
    config["mode"] = 2
    sys.setrecursionlimit(1000000)

    branch_result, leaf_result = \
        branch_leaf_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
    print("---------------Result---------------")
    print("false_positive_number = {}\n"
          "true_negative_number  = {}\n"
          "matched_mean_distance = {}\n"
          "pt_score              = {}".format(branch_result[0], branch_result[1], branch_result[2], branch_result[3]))
    print("----------------End-----------------")

