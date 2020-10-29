import sys

from anytree import NodeMixin, iterators, RenderTree, PreOrderIter
from pyneval.model.euclidean_point import EuclideanPoint,Line
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.edge_match_utils import get_match_edges
from pyneval.metric.utils.config_utils import get_default_threshold
from pyneval.io.read_json import read_json
from pyneval.io.save_swc import save_as_swc
from pyneval.io.read_swc import adjust_swcfile
from pyneval.io.read_config import read_float_config, read_path_config
# from test.test_model.length_metric.cprofile_test import do_cprofile

import time
import os, platform


def length_metric_2(gold_swc_tree=None, test_swc_tree=None,
                    rad_threshold=-1.0, len_threshold=0.2, detail_path=None, DEBUG=True):
    vertical_tree = []

    match_edges, test_match_length = get_match_edges(gold_swc_tree, test_swc_tree,  # tree data
                                                  vertical_tree,  # a empty tree helps
                                                  rad_threshold, len_threshold, detail_path, DEBUG=False)  # configs

    match_length = 0.0
    for line_tuple in match_edges:
        match_length += line_tuple[0].parent_distance()

    gold_total_length = round(gold_swc_tree.length(), 8)
    test_total_length = round(test_swc_tree.length(), 8)
    match_length = round(match_length, 8)
    test_match_length = round(test_match_length, 8)

    if DEBUG:
        print("match_length a = {}, gold_total_length = {}, test_total_length = {}"
              .format(match_length, gold_total_length, test_total_length))
    if gold_total_length != 0:
        recall = round(match_length/gold_total_length, 8)
    else:
        recall = 0

    if test_total_length != 0:
        precision = round(test_match_length/test_total_length, 8)
    else:
        precision = 0
    return min(recall, 1.0), min(precision, 1.0), vertical_tree


def length_metric_1(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    gold_total_length = gold_swc_tree.length()
    test_total_length = test_swc_tree.length()

    if DEBUG:
        print("gold_total_length = {}, test_total_length = {}"
              .format(gold_total_length, test_total_length))
    return 1 - test_total_length/gold_total_length


# @do_cprofile("./mkm_run.prof")
def length_metric(gold_swc_tree, test_swc_tree, abs_dir, config):
    # remove old pot mark
    gold_swc_tree.type_clear(5)
    test_swc_tree.type_clear(4)

    # get config threshold
    rad_threshold = read_float_config(config=config, config_name="rad_threshold", default=-1.0)
    len_threshold = read_float_config(config=config, config_name="len_threshold", default=0.2)

    # get config detail path
    detail_path = read_path_config(config=config, config_name="detail", abs_dir=abs_dir, default=None)

    # get config method
    if config["method"] == 1:
        ratio = length_metric_1(gold_swc_tree=gold_swc_tree,
                                test_swc_tree=test_swc_tree)
        print("1 - test_length / gold_length= {}".format(ratio))
        return ratio
    elif config["method"] == 2:
        # check every edge in test, if it is overlap with any edge in gold three
        recall, precision, vertical_tree = length_metric_2(gold_swc_tree=test_swc_tree,
                                                           test_swc_tree=gold_swc_tree,
                                                           rad_threshold=rad_threshold,
                                                           len_threshold=len_threshold,
                                                           detail_path=detail_path,
                                                           DEBUG=True)
        # print("Recall = {}, Precision = {}".format(recall, precision))
        return tuple([recall, precision, "".join(vertical_tree)])
    else:
        raise Exception("[Error: ] Read config info method {}. length metric only have 1 and 2 two methods".format(
            config["method"]
        ))


# length metric interface connect to webmets
def pyneval_length_metric(gold_swc, test_swc, method, rad_threshold, len_threshold):
    gold_tree = SwcTree()
    test_tree = SwcTree()

    gold_tree.load_list(adjust_swcfile(gold_swc))
    test_tree.load_list(adjust_swcfile(test_swc))

    config = {
        'method': method,
        'len_threshold': len_threshold,
        'rad_threshold': rad_threshold
    }

    lm_res = length_metric(gold_swc_tree=gold_tree,
                           test_swc_tree=test_tree,
                           abs_dir="",
                           config=config)

    result = {
        'recall': lm_res[0],
        'precision': lm_res[1],
        'gold_swc': gold_tree.to_str_list(),
        'test_swc': test_tree.to_str_list(),
        'vertical_swc': lm_res[2]
    }
    return result


if __name__ == "__main__":
    goldTree = SwcTree()
    testTree = SwcTree()
    sys.setrecursionlimit(10000000)
    goldTree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\194444.swc")
    testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\194444.swc")
    # print(len(goldTree.root().children))

    lm_res = length_metric(gold_swc_tree=goldTree,
                           test_swc_tree=testTree,
                           abs_dir="D:\gitProject\mine\PyNeval",
                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

    print(lm_res[0], lm_res[1])