from src.model.swc_node import SwcTree,get_match_edges,get_default_threshold
from src.io.read_json import read_json
import time

def length_metric_2(gold_swc_tree=None, test_swc_tree=None, knn=3, DEBUG=False):
    match_edge = get_match_edges(gold_swc_tree=gold_swc_tree,
                                 test_swc_tree=test_swc_tree,
                                 knn=knn,
                                 DEBUG=DEBUG)
    match_lenth = 0.0
    for gold_edge in match_edge.keys():
        son_node = gold_edge[1]
        match_lenth += son_node.parent_distance()

    total_length = gold_swc_tree.length()

    print("match length = {}, total_length = {}".format(match_lenth, total_length))
    return match_lenth/total_length


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
    testTree.align_roots(goldtree)
    start = time.time()
    print(length_metric(test_swc_tree=testTree, gold_swc_tree=goldtree,config=read_json("D:\gitProject\mine\PyMets\\test\length_metric.json")))
    print(time.time() - start)