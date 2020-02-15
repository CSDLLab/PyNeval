from anytree import NodeMixin, iterators, RenderTree, PreOrderIter
from pymets.model.euclidean_point import EuclideanPoint,Line
from pymets.model.swc_node import SwcTree
from pymets.metric.utils.edge_match_utils import get_match_edges_e_fast
from pymets.metric.utils.config_utils import get_default_threshold
from pymets.io.read_json import read_json
from pymets.io.save_swc import save_as_swc,print_swc

import time
import os,platform


def length_metric_2(gold_swc_tree=None, test_swc_tree=None, dis_threshold=0.1, detail_path=None, DEBUG=True):
    test_swc_tree.get_lca_preprocess()
    match_edges, un_match_edges = get_match_edges_e_fast(gold_swc_tree, test_swc_tree,  # tree data
                                                         dis_threshold, detail_path, DEBUG=False)  # configs

    save_as_swc(object=un_match_edges, file_path=detail_path)
    match_length = 0.0
    for line_tuple in match_edges:
        match_length += line_tuple[0].parent_distance()

    gold_total_length = round(gold_swc_tree.length(), 8)
    test_total_length = round(test_swc_tree.length(), 8)
    match_length = round(match_length, 8)

    if DEBUG:
        print("match_length a = {}, gold_total_length = {}, test_total_length = {}"
              .format(match_length, gold_total_length, test_total_length))
    return match_length/gold_total_length, match_length/test_total_length


def length_metric_1(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    gold_total_length = gold_swc_tree.length()
    test_total_length = test_swc_tree.length()

    if DEBUG:
        print("gold_total_length = {}, test_total_length = {}"
              .format(gold_total_length, test_total_length))
    return 1 - test_total_length/gold_total_length


def length_metric(gold_swc_tree, test_swc_tree, abs_dir, config):
    # get config threshold
    if "threshold" not in config.keys() or config["threshold"] == "default":
        dis_threshold = get_default_threshold(gold_swc_tree)
    else:
        try:
            dis_threshold = float(config["threshold"])
        except:
            raise Exception("[Error: ] Read config info threshold {}. suppose to be a float or \"default\"")
    # get config detail path
    detail_path = config["detail"]
    if platform.system() == "Linux":
        detail_path = '/'.join(detail_path.split("\\"))
    detail_path = os.path.join(abs_dir, detail_path)
    if os.path.exists(detail_path):
        os.remove(detail_path)
    # get config method
    if config["method"] == 1:
        ratio = length_metric_1(gold_swc_tree=gold_swc_tree,
                                test_swc_tree=test_swc_tree)
        print("1 - test_length / gold_length= {}".format(ratio))
    elif config["method"] == 2:
        recall, Precision = length_metric_2(gold_swc_tree=gold_swc_tree,
                                            test_swc_tree=test_swc_tree,
                                            dis_threshold=dis_threshold,
                                            detail_path=detail_path,
                                            DEBUG=True)
        print("Recall = {}, Precision = {}".format(recall, Precision))
    else:
        raise Exception("[Error: ] Read config info method {}. length metric only have 1 and 2 two methods")


if __name__ == "__main__":
    goldtree = SwcTree()

    testTree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\multy_useage\\useage1.swc")
    testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\multy_useage\\useage1.swc")

    start = time.time()
    length_metric(gold_swc_tree=goldtree,
                  test_swc_tree=testTree,
                  abs_dir="D:\gitProject\mine\PyMets",
                  config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
    length_metric(gold_swc_tree=testTree,
                  test_swc_tree=goldtree,
                  abs_dir="D:\gitProject\mine\PyMets",
                  config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
    print("time cost = {}".format(time.time() - start))