import sys

from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.km_utils import KM
from pyneval.io.read_json import read_json
import numpy as np


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
        if len(node.children) > 1:
            branch_list.append(node)
    return branch_list


def get_leaf_swc_list(swc_tree):
    swc_list = swc_tree.get_node_list()
    leaf_list = []
    for node in swc_list:
        if len(node.children) == 0:
            leaf_list.append(node)
    return leaf_list


def score(test_node_list, gold_node_list, threshold_dis):
    switch = False
    test_len = len(test_node_list)
    gold_len = len(gold_node_list)

    if gold_len < test_len:
        switch = True
        test_len, gold_len = gold_len, test_len
        test_node_list, gold_node_list = gold_node_list, test_node_list

    dis_graph = np.zeros(shape=(max(test_len+1, gold_len+1), max(test_len+1, gold_len+1)))

    for i in range(test_len):
        for j in range(gold_len):
            dis = test_node_list[i].distance(gold_node_list[j])
            if dis < threshold_dis:
                dis_graph[i][j] = -dis
            else:
                dis_graph[i][j] = -0x3f3f3f3f/2

    dis_graph = dis_graph.tolist()

    km = KM(maxn=max(test_len, gold_len)+10, nx=test_len, ny=gold_len, G=dis_graph)
    km.solve()
    false_pos_num, true_neg_num, true_pos_num = 0, 0, 0
    for i in range(0, gold_len):
        if km.match[i] != -1 and km.G[km.match[i]][i] != -0x3f3f3f3f/2:
            true_pos_num += 1
    false_pos_num = gold_len - true_pos_num
    true_neg_num = test_len - true_pos_num
    if switch:
        true_neg_num, false_pos_num = false_pos_num, true_neg_num

    if true_pos_num != 0:
        mean_dis = -km.get_max_dis() / true_pos_num
    else:
        mean_dis = 0
    pt_cost = -km.get_max_dis() + threshold_dis * (false_pos_num + true_neg_num) / (false_pos_num + true_neg_num + true_pos_num)

    # print("output")
    # print(false_pos_num)
    # print(true_neg_num)
    # print(mean_dis)
    # print(pt_cost)
    return false_pos_num, true_neg_num, mean_dis, pt_cost


def branch_leaf_metric(test_swc_tree, gold_swc_tree, config):
    threshold_dis = config["threshold_dis"]
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
    leaf_result = score(test_node_list=test_leaf_swc_list,
                        gold_node_list=gold_leaf_swc_list,
                        threshold_dis=threshold_dis)
    branch_result = score(test_node_list=test_branch_swc_list,
                          gold_node_list=gold_branch_swc_list,
                          threshold_dis=threshold_dis)

    return branch_result, leaf_result


if __name__ == "__main__":
    gold_swc_tree = SwcTree()
    test_swc_tree = SwcTree()
    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\branch_metric\\branch4.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\branch_metric\\branch4.swc")
    test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\194444_new.swc")
    gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\194444.swc")
    config = read_json("D:\gitProject\\mine\\PyNeval\\config\\branch_metric.json")
    sys.setrecursionlimit(1000000)

    branch_result, leaf_result = \
        branch_leaf_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
    print("{} {} {} {}".format(branch_result[0], branch_result[1], branch_result[2], branch_result[3]))