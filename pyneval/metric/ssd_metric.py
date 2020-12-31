# -*- coding: utf-8 -*-
"""a geometry metric method, SSD metric

This module implement a geometry metric method called Substantial Spatial Distance.
SSD method was firstly
"""
import sys

from pyneval.model.swc_node import SwcTree
from pyneval.io.read_json import read_json
from pyneval.tools.re_sample import up_sample_swc_tree
from pyneval.io.save_swc import swc_save
from pyneval.metric.utils.point_match_utils import create_kdtree
from pyneval.io.read_config import read_bool_config


def get_mse(src_tree, tar_tree, min_threshold):
    dis, num = 0, 0
    kdtree, pos_node_dict = create_kdtree(tar_tree.get_node_list())
    for node in src_tree.get_node_list():
        if node.is_virtual():
            continue
        target_pos = kdtree.search_knn(list(node.get_center_as_tuple()), k=1)[0]
        target_node = pos_node_dict[tuple(target_pos[0].data)]

        cur_dis = target_node.distance(node)
        if cur_dis >= min_threshold:
            dis += cur_dis
            num += 1
    dis /= num
    return dis, num


def ssd_metric(gold_swc_tree, test_swc_tree, config):
    debug = read_bool_config(config=config, config_name="debug", default=False)
    if debug:
        print("[Debug: ] In ssd metric")

    u_gold_swc_tree = up_sample_swc_tree(gold_swc_tree, thres_length=1.0)
    u_test_swc_tree = up_sample_swc_tree(test_swc_tree, thres_length=1.0)

    if config["detail_path"] is not None:
        swc_save(u_gold_swc_tree, config["detail_path"][:-4] + "_gold_upsampled.swc")
        swc_save(u_test_swc_tree, config["detail_path"][:-4] + "_test_upsampled.swc")

    g2t_score, g2t_num = get_mse(u_gold_swc_tree, u_test_swc_tree, config["min_threshold"])
    t2g_score, t2g_num = get_mse(u_test_swc_tree, u_gold_swc_tree, config["min_threshold"])

    avg_score = (g2t_score + t2g_score) / 2
    return avg_score, g2t_num/u_gold_swc_tree.size(), t2g_num/u_test_swc_tree.size()


if __name__ == "__main__":
    test_tree = SwcTree()
    gold_tree = SwcTree()

    sys.setrecursionlimit(10000000)
    gold_tree.load("..\\..\\data\\test_data\\ssd_data\\gold\\c.swc")
    test_tree.load("..\\..\\data\\test_data\\ssd_data\\test\\c.swc")
    config = read_json("..\\..\\config\\ssd_metric.json")

    score, per1, per2 = ssd_metric(gold_swc_tree=gold_tree,
                                   test_swc_tree=test_tree,
                                   config=config)
    print("ssd score    = {}\nssd% of gold = {}%\nssd% of test = {}%".
          format(round(score, 2), round(per1*100, 2), round(per2*100, 2)))

