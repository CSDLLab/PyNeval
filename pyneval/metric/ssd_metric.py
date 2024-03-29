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

import jsonschema

from pyneval.model import swc_node
from pyneval.model import swc_tree
from pyneval.tools import re_sample
from pyneval.metric.utils import point_match_utils
from pyneval.metric.utils import basic_utils
from pyneval.metric.utils.metric_manager import get_metric_manager

metric_manager = get_metric_manager()


class SsdMetric(object):
    """
    ssd metric
    """

    def __init__(self, config):
        self.debug = config["debug"] if config.get("debug") is not None else False
        self.threshold_mode = config["threshold_mode"]
        self.ssd_threshold = config["ssd_threshold"]
        self.up_sample_threshold = config["up_sample_threshold"]
        self.scale = config["scale"]

    def get_mse(self, src_tree, tar_tree, ssd_threshold=2.0, mode=1):
        """ calculate the minimum square error of two trees
        find the closest node on the tar_tree for each node on the src tree, calculate the average
        distance of these node pairs.

        Args:
            src_tree(SwcTree):
            tar_tree(SwcTree):
            ssd_threshold(float): distance will be count into the res
                only if two nodes' distance is larger than this threshold.
            mode(1 or 2):
                1 means static threshold, equal to ssd_threshold.
                2 means dynamic threshold, equal to ssd_threshold * src_node.threshold

        Returns:
            dis(float): average minimum distance of node, distance must be larger than ssd_threshold
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

            if mode == 1:
                threshold = ssd_threshold
            else:
                threshold = ssd_threshold * node.radius()

            if cur_dis >= threshold:
                node._type = 9
                dis += cur_dis
                num += 1
        try:
            dis /= num
        except ZeroDivisionError:
            dis = num = 0
        return dis, num

    def run(self, gold_swc_tree, test_swc_tree):
        gold_swc_tree.rescale(self.scale)
        test_swc_tree.rescale(self.scale)
        u_gold_swc_tree = re_sample.up_sample_swc_tree(swc_tree=gold_swc_tree,
                                                       length_threshold=self.up_sample_threshold)
        u_test_swc_tree = re_sample.up_sample_swc_tree(swc_tree=test_swc_tree,
                                                       length_threshold=self.up_sample_threshold)
        u_gold_swc_tree.set_node_type_by_topo(root_id=1)
        u_test_swc_tree.set_node_type_by_topo(root_id=5)

        g2t_score, g2t_num = self.get_mse(src_tree=u_gold_swc_tree, tar_tree=u_test_swc_tree,
                                     ssd_threshold=self.ssd_threshold, mode=self.threshold_mode)
        t2g_score, t2g_num = self.get_mse(src_tree=u_test_swc_tree, tar_tree=u_gold_swc_tree,
                                     ssd_threshold=self.ssd_threshold, mode=self.threshold_mode)

        if self.debug:
            print("recall_num = {}, pre_num = {}, gold_tot_num = {}, test_tot_num = {} {} {}".format(
                g2t_num, t2g_num, u_gold_swc_tree.size(), u_test_swc_tree.size(), gold_swc_tree.length(),
                test_swc_tree.length()
            ))

        res = {
            "ssd_score": (g2t_score + t2g_score) / 2,
            "recall": 1 - g2t_num / u_gold_swc_tree.size(),
            "precision": 1 - t2g_num / u_test_swc_tree.size(),
            "f1_score": basic_utils.get_f1score(
                recall=1 - g2t_num / u_gold_swc_tree.size(),
                precision=1 - t2g_num / u_test_swc_tree.size()
            )
        }

        return res, u_gold_swc_tree, u_test_swc_tree


@metric_manager.register(
    name="ssd",
    config="ssd_metric.json",
    desc="minimum square error between resampled gold and test trees",
    alias=['SM'],
    public=True,
)
def ssd_metric(gold_swc_tree: swc_tree.SwcTree, test_swc_tree: swc_tree.SwcTree, config: dict):
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
    ssd = SsdMetric(config)
    return ssd.run(gold_swc_tree, test_swc_tree)
