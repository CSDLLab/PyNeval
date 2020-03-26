from anytree import NodeMixin, iterators, RenderTree, PreOrderIter
from pymets.model.euclidean_point import EuclideanPoint,Line
from pymets.model.swc_node import SwcTree
from pymets.metric.utils.edge_match_utils import get_match_edges
from pymets.metric.utils.config_utils import get_default_threshold
from pymets.io.read_json import read_json
from pymets.io.save_swc import save_as_swc, swc_to_list
from pymets.io.read_swc import adjust_swcfile

import time
import os,platform


def length_metric_2(gold_swc_tree=None, test_swc_tree=None,
                    rad_threshold=-1.0, len_threshold=0.2, detail_path=None, DEBUG=True):
    vertical_tree = SwcTree()

    test_swc_tree.get_lca_preprocess()
    match_edges, un_match_edges = get_match_edges(gold_swc_tree, test_swc_tree,  # tree data
                                                  vertical_tree, # a empty tree helps
                                                  rad_threshold, len_threshold, detail_path, DEBUG=False)  # configs
    if detail_path is not None:
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
    # remove old point mark
    gold_swc_tree.type_clear(5)
    test_swc_tree.type_clear(4)

    # get config threshold
    if "rad_threshold" not in config.keys() or config["rad_threshold"] == "default":
        rad_threshold = -1.0
    else:
        try:
            rad_threshold = float(config["rad_threshold"])
        except:
            raise Exception("[Error: ] Read config info threshold {}. suppose to be a float or \"default\"")

    if "len_threshold" not in config.keys() or config["len_threshold"] == "default":
        len_threshold = 0.2
    else:
        try:
            len_threshold = float(config["len_threshold"])
        except:
            raise Exception("[Error: ] Read config info threshold {}. suppose to be a float or \"default\"")

    # get config detail path
    if "detail" in config.keys():
        detail_path = config["detail"]
        if platform.system() == "Linux":
            detail_path = '/'.join(detail_path.split("\\"))
        detail_path = os.path.join(abs_dir, detail_path)
        if os.path.exists(detail_path):
            os.remove(detail_path)
    else:
        detail_path = None

    # get config method
    if config["method"] == 1:
        ratio = length_metric_1(gold_swc_tree=gold_swc_tree,
                                test_swc_tree=test_swc_tree)
        print("1 - test_length / gold_length= {}".format(ratio))
        return ratio
    elif config["method"] == 2:
        # check every edge in test, if it is overlap with any edge in gold three
        recall, precision = length_metric_2(gold_swc_tree=test_swc_tree,
                                            test_swc_tree=gold_swc_tree,
                                            rad_threshold=rad_threshold,
                                            len_threshold=len_threshold,
                                            detail_path=detail_path,
                                            DEBUG=False)
        print("Recall = {}, Precision = {}".format(recall, precision))
        return recall, precision
    else:
        raise Exception("[Error: ] Read config info method {}. length metric only have 1 and 2 two methods".format(
            config["method"]
        ))


# length metric interface connect to webmets
def web_length_metric(gold_swc, test_swc, method, rad_threshold, len_threshold):
    gold_tree = SwcTree()
    test_tree = SwcTree()

    gold_tree.load_list(adjust_swcfile(gold_swc))
    test_tree.load_list(adjust_swcfile(test_swc))

    config = {
        'method': method,
        'len_threshold': len_threshold,
        'rad_threshold': rad_threshold
    }

    recall, precision = length_metric(gold_swc_tree=gold_tree,
                                      test_swc_tree=test_tree,
                                      abs_dir="",
                                      config=config)
    # gold_tree.radius_limit(10)
    # test_tree.radius_limit(10)

    result = {
        'recall': recall,
        'precision': precision,
        'gold_swc': swc_to_list(gold_tree),
        'test_swc': swc_to_list(test_tree)
    }
    return result


if __name__ == "__main__":
    goldtree = SwcTree()

    testTree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\2_18_gold.swc")
    testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\2_18_test.swc")

    start = time.time()
    # length_metric(gold_swc_tree=goldtree,
    #               test_swc_tree=testTree,
    #               abs_dir="D:\gitProject\mine\PyMets",
    #               config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
    length_metric(gold_swc_tree=testTree,
                  test_swc_tree=goldtree,
                  abs_dir="D:\gitProject\mine\PyMets",
                  config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
    print("time cost = {}".format(time.time() - start))