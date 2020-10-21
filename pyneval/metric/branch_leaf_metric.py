import copy
import sys
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.km_utils import KM, get_dis_graph
from pyneval.io.read_json import read_json
from pyneval.metric.utils.point_match_utils import get_gold_test_dicts


def debug_out_list(swc_list, _str):
    print("[debug_out_list ]" + _str + str(len(swc_list)))
    for node in swc_list:
        print(node.get_id(), end=" ")
    print("")


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
    return true_pos_num, false_pos_num, true_neg_num, mean_dis, -km.get_max_dis(), pt_cost


def score_point_distance(gold_tree, test_tree, test_node_list, test_gold_dict, gold_node_list, threshold_dis, mode):
    # disgraph is a 2D ndarray store the distance of nodes in gold and test
    # test_node_list contains only branch or leaf nodes
    dis_graph, switch, test_len, gold_len = get_dis_graph(gold_tree=gold_tree,
                                                          test_tree=test_tree,
                                                          test_node_list=test_node_list,
                                                          gold_node_list=gold_node_list,
                                                          test_gold_dict=test_gold_dict,
                                                          threshold_dis=threshold_dis,
                                                          mode=mode)

    km = KM(maxn=max(test_len, gold_len)+10, nx=test_len, ny=gold_len, G=dis_graph)
    km.solve()

    true_pos_num, false_pos_num, true_neg_num, \
    mean_dis, tot_dis, pt_cost = get_result(test_len=test_len,
                                            gold_len=gold_len,
                                            switch=switch,
                                            km=km,
                                            threshold_dis=threshold_dis)
    # calculate the number of isolated nodes
    iso_node_num = 0
    for node in test_swc_tree.get_node_list():
        if node.is_isolated():
            iso_node_num += 1
    return gold_len, test_len, true_pos_num, false_pos_num, true_neg_num, mean_dis, tot_dis, pt_cost, iso_node_num


def branch_leaf_metric(test_swc_tree, gold_swc_tree, config):
    threshold_dis = config["threshold_dis"]
    mode = config["mode"]
    test_branch_swc_list = get_branch_swc_list(test_swc_tree)
    gold_branch_swc_list = get_branch_swc_list(gold_swc_tree)
    test_leaf_swc_list = get_leaf_swc_list(test_swc_tree)
    gold_leaf_swc_list = get_leaf_swc_list(gold_swc_tree)
    gold_test_dict, test_gold_dict = get_gold_test_dicts(gold_node_list=gold_swc_tree.get_node_list(),
                                                         test_node_list=test_swc_tree.get_node_list())
    # debug output
    # debug_out_list(test_branch_swc_list, "test_branch_swc_list")
    # debug_out_list(gold_branch_swc_list, "gold_branch_swc_list")
    # debug_out_list(test_leaf_swc_list, "test_leaf_swc_list")
    # debug_out_list(gold_leaf_swc_list, "gold_leaf_swc_list")

    # result[0]:gold_len
    # result[1]:test_len
    # result[2]:true_pos_num
    # result[3]:false_pos_num
    # result[4]:true_neg_num
    # result[5]:mean_dis
    # result[6]:tot_dis
    # result[7]:pt_cost
    leaf_result = score_point_distance(gold_tree=gold_swc_tree,
                                       test_tree=test_swc_tree,
                                       test_node_list=test_leaf_swc_list,
                                       gold_node_list=gold_leaf_swc_list,
                                       test_gold_dict=test_gold_dict,
                                       threshold_dis=threshold_dis,
                                       mode=mode)
    branch_result = score_point_distance(gold_tree=gold_swc_tree,
                                         test_tree=test_swc_tree,
                                         test_node_list=test_branch_swc_list,
                                         gold_node_list=gold_branch_swc_list,
                                         test_gold_dict=test_gold_dict,
                                         threshold_dis=threshold_dis,
                                         mode=mode)

    return branch_result, leaf_result


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    gold_swc_tree = SwcTree()
    test_swc_tree = SwcTree()
    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\branch_metric\\branch4.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\branch_metric\\branch4.swc")
    test_swc_tree.load("..\\..\\data\\branch_metric_data\\test\\194444_isolated_node.swc")
    gold_swc_tree.load("..\\..\\data\\branch_metric_data\\gold\\194444.swc")

    config = read_json("..\\..\\config\\branch_metric.json")
    config["mode"] = 2
    branch_result, leaf_result = \
        branch_leaf_metric(test_swc_tree=test_swc_tree, gold_swc_tree=gold_swc_tree, config=config)
    print("---------------Result---------------")
    print("gole_branch_num = {}, test_branch_num = {}\n"
          "true_positive_number  = {}\n"
          "false_positive_number = {}\n"
          "true_negative_number  = {}\n"
          "matched_mean_distance = {}\n"
          "matched_sum_distance  = {}\n"
          "pt_score              = {}\n"
          "isolated node numbers = {}".format(branch_result[0], branch_result[1], branch_result[2],
                                              branch_result[3], branch_result[4], branch_result[5],
                                              branch_result[6], branch_result[7], branch_result[8]))
    print("----------------End-----------------")

