from anytree import NodeMixin, iterators, RenderTree, PreOrderIter
from pymets.model.euclidean_point import EuclideanPoint,Line
from pymets.model.swc_node import SwcTree
from pymets.metric.utils.edge_match_utils import get_unmatch_edges_e,get_match_edges_e_fast
from pymets.metric.utils.config_utils import get_default_threshold
from pymets.io.read_json import read_json
from pymets.io.save_swc import save_as_swc,print_swc

import time
import os


def length_metric_3(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    test_swc_tree.get_lca_preprocess()
    match_fail = get_unmatch_edges_e(gold_swc_tree, test_swc_tree)

    return match_fail


def length_metric_2(gold_swc_tree=None, test_swc_tree=None, dis_threshold=0.1, detail_path=None, DEBUG=True):
    match_edges = get_match_edges_e_fast(gold_swc_tree, test_swc_tree,  # tree data
                                         dis_threshold, detail_path, DEBUG=DEBUG)  # configs

    match_length = 0.0
    for line_tuple in match_edges:
        match_length += line_tuple[0].parent_distance()

    gold_total_length = round(gold_swc_tree.length(), 8)
    match_length = round(match_length, 8)

    if DEBUG:
        print("match_length a = {}, gold_total_length = {}"
              .format(match_length, gold_total_length))
    return match_length/gold_total_length


def length_metric_1(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    gold_total_length = gold_swc_tree.length()
    test_total_length = test_swc_tree.length()

    if DEBUG:
        print("gold_total_length = {}, test_total_length = {}"
              .format(gold_total_length, test_total_length))
    return 1 - test_total_length/gold_total_length


def length_metric(gold_swc_tree, test_swc_tree, abs_dir, config):
    if "knn" in config.keys():
        knn = config["knn"]

    dis_threshold = 0.1
    if "thereshold" not in config.keys() or config["thereshold"] == "default":
        dis_threshold = get_default_threshold(gold_swc_tree)
    else:
        try:
            dis_threshold = float(config["thereshold"])
        except:
            raise Exception("[Error: ] Read config info threshold {}. suppose to be a float or \"default\"")

    detail_path = config["detail"]
    detail_path = os.path.join(abs_dir, detail_path)
    if config["method"] == 1:
        return length_metric_1(gold_swc_tree=gold_swc_tree,
                               test_swc_tree=test_swc_tree)
    elif config["method"] == 2:
        print("result = {}".format(length_metric_2(gold_swc_tree=gold_swc_tree,
                                test_swc_tree=test_swc_tree,
                                dis_threshold=dis_threshold,
                                detail_path=detail_path,
                                DEBUG=False)))
    elif config["method"] == 3:
        match_fail_tuple_set = length_metric_3(gold_swc_tree=gold_swc_tree,
                                                test_swc_tree=test_swc_tree,
                                                DEBUG=False)
        if config["detail"] != "":
            save_as_swc(match_fail_tuple_set, config["detail"])
        else:
            print_swc(match_fail_tuple_set)
        return True
    else:
        raise Exception("[Error: ] Read config info method {}. length metric only have 1 and 2 two methods")


if __name__ == "__main__":
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\ExampleGoldStandard.swc")

    testTree = SwcTree()
    testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\ExampleTest.swc")
    start = time.time()
    length_metric(gold_swc_tree=goldtree,
                  test_swc_tree=testTree,
                  abs_dir="D:\gitProject\mine\PyMets",
                  config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
    # length_metric(gold_swc_tree=testTree,
    #               test_swc_tree=goldtree,
    #               abs_dir="D:\gitProject\mine\PyMets",
    #               config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
    print("time cost = {}".format(time.time() - start))