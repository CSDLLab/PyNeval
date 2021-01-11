# -*- coding: utf-8 -*-
"""a geometry metric method, SSD metric

This module implement a geometry metric method called Substantial Spatial Distance.
relative paper: https://doi.org/10.1038/nbt.1612
title, auther

Example:
    In command line:
    $ pyneval --gold ./data\\test_data\\ssd_data\\gold\\c.swc
              --test .\\data\\test_data\\ssd_data\\test\\c.swc
              --metric ssd_metric
Attributes:
    None

Todos:
    None
"""
import sys

from pyneval.io import swc_writer
from pyneval.model import swc_node
from pyneval.io import read_json
from pyneval.tools import re_sample
from pyneval.metric.utils import point_match_utils
from pyneval.io import read_config


def get_mse(src_tree, tar_tree, min_threshold):
    """ calculate the minimum square error of two trees
    find the closest node on the tar_tree for each node on the src tree, calculate the average
    distance of these node pairs.

    Args:
        src_tree(SwcTree):
        tar_tree(SwcTree):
        min_threshold(float): distance will be count into the res
            only if two nodes' distance is larger than this threshold.

    Returns:
        dis(float): average minimum distance of node, distance must be larger than min_threshold
        num(float): The number of pairs of nodes that are counted when calculating distance

    Raise:
        None
    """
    dis, num = 0, 0
    kdtree, pos_node_dict = point_match_utils.create_kdtree(tar_tree.get_node_list())
    for node in src_tree.get_node_list():
        if node.is_virtual():
            continue
        target_pos = kdtree.search_knn(list(node.get_center_as_tuple()), k=1)[0]
        target_node = pos_node_dict[tuple(target_pos[0].data)]

        cur_dis = target_node.distance(node)
        if cur_dis >= min_threshold:
            node._type = 9
            dis += cur_dis
            num += 1
    try:
        dis /= num
    except ZeroDivisionError:
        dis = num = 0
    return dis, num


def ssd_metric(gold_swc_tree: swc_node.SwcTree, test_swc_tree: swc_node.SwcTree, config: dict):
    """Main function of SSD metric.
    Args:
        gold_swc_tree(SwcTree):
        test_swc_tree(SwcTree):
        config(Dict):
            The keys of 'config' is the name of configs, and the items are config values
    Example:
        test_tree = swc_node.SwcTree()
        gold_tree = swc_node.SwcTree()
        gold_tree.load("..\\..\\data\\test_data\\ssd_data\\gold\\c.swc")
        test_tree.load("..\\..\\data\\test_data\\ssd_data\\test\\c.swc")
        score, recall, precision = ssd_metric(gold_swc_tree=gold_tree,
                                              test_swc_tree=test_tree,
                                              config=config)
    Returns:
        tuple: contain three values to demonstrate metric result
            avg_score(float): average distance of nodes between gold and test swc trees.
            precision(float): percentage of nodes that are matched compared to test tree
            recall(float): percentage of nodes that are matched compared to gold tree

    Raises:
        None
    """
    debug = read_config.read_bool_config(config=config, config_name="debug", default=False)
    if debug:
        print("[Debug: ] In ssd metric")

    u_gold_swc_tree = re_sample.up_sample_swc_tree(gold_swc_tree, thres_length=1.0)
    u_test_swc_tree = re_sample.up_sample_swc_tree(test_swc_tree, thres_length=1.0)
    u_gold_swc_tree.set_node_type_by_topo(root_id=1)
    u_test_swc_tree.set_node_type_by_topo(root_id=5)

    g2t_score, g2t_num = get_mse(u_gold_swc_tree, u_test_swc_tree, config["min_threshold"])
    t2g_score, t2g_num = get_mse(u_test_swc_tree, u_gold_swc_tree, config["min_threshold"])

    if config["detail_path"] is not None:
        swc_writer.swc_save(u_gold_swc_tree, config["detail_path"][:-4] + "_gold_upsampled.swc")
        swc_writer.swc_save(u_test_swc_tree, config["detail_path"][:-4] + "_test_upsampled.swc")

    avg_score = (g2t_score + t2g_score) / 2
    recall = 1 - g2t_num/u_gold_swc_tree.size()
    precision = 1 - t2g_num/u_test_swc_tree.size()
    return avg_score, recall, precision


if __name__ == "__main__":
    test_tree = swc_node.SwcTree()
    gold_tree = swc_node.SwcTree()

    sys.setrecursionlimit(10000000)
    gold_tree.load("..\\..\\data\\test_data\\geo_metric_data\\gold_fake_data5.swc")
    test_tree.load("..\\..\\data\\test_data\\geo_metric_data\\test_fake_data5.swc")
    config = read_json.read_json("..\\..\\config\\ssd_metric.json")

    score, recall, precision = ssd_metric(gold_swc_tree=gold_tree,
                                          test_swc_tree=test_tree,
                                          config=config)
    print("ssd score = {}\n"
          "recall    = {}%\n"
          "precision = {}%".
          format(round(score, 2), round(recall*100, 2), round(precision*100, 2)))

