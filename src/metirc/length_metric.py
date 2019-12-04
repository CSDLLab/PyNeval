from anytree import NodeMixin, iterators, RenderTree, PreOrderIter
from src.model.euclidean_point import EuclideanPoint,Line
from src.model.swc_node import SwcTree,get_match_edges_e,get_default_threshold,dis_threshold
from src.io.read_json import read_json
import time


def length_metric_2(gold_swc_tree=None, test_swc_tree=None, knn=3, DEBUG=False):
    match_edges = get_match_edges_e(gold_swc_tree, test_swc_tree)
    match_length = 0.0
    for line_tuple in match_edges:
        match_length += line_tuple[0].parent_distance()

    gold_total_length = gold_swc_tree.length()
    if DEBUG:
        print("match_length = {}, gold_total_length = {}"
              .format(match_length, gold_total_length))
    return match_length/gold_total_length


def length_metric_1(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    gold_total_length = gold_swc_tree.length()
    test_total_length = test_swc_tree.length()

    if DEBUG:
        print("gold_total_length = {}, test_total_length = {}"
              .format(gold_total_length, test_total_length))
    return 1 - test_total_length/gold_total_length


def length_metric(gold_swc_tree, test_swc_tree, config):
    global dis_threshold
    knn = 3

    if "knn" in config.keys():
        knn = config["knn"]

    if "thereshold" not in config.keys() or config["thereshold"] == "default":
        get_default_threshold(gold_swc_tree)
    else:
        try:
            dis_threshold = float(config["thereshold"])
            print(dis_threshold)
        except:
            raise Exception("[Error: ] Read config info threshold {}. suppose to be a float or \"default\"")

    if config["method"] == 1:
        return length_metric_1(gold_swc_tree=gold_swc_tree,
                               test_swc_tree=test_swc_tree)
    elif config["method"] == 2:
        return length_metric_2(gold_swc_tree=gold_swc_tree,
                               test_swc_tree=test_swc_tree,
                               knn=knn,
                               DEBUG=False)
    else:
        raise Exception("[Error: ] Read config info method {}. length metric only have 1 and 2 two methods")



if __name__ == "__main__":
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\ExampleGoldStandard.swc")
    get_default_threshold(goldtree)

    testTree = SwcTree()
    testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\ExampleTest.swc")
    # testTree.align_roots(goldtree,mode="average",DEBUG=True)
    start = time.time()
    print(length_metric(test_swc_tree=testTree, gold_swc_tree=goldtree,config=read_json("D:\gitProject\mine\PyMets\\test\length_metric.json")))
    print(time.time() - start)