from anytree import PreOrderIter
from src.model.swc_node import SwcTree,SwcNode
import kdtree
import queue
import time

K_NN = 3
dis_threshold = 0.1


def get_kdtree_data(kd_node):
    return kd_node[0].data


def check_match(gold_node_knn, son_node_knn, edge_set, id_center_dict):
    for pa in gold_node_knn:
        test_pa_node = id_center_dict[tuple(get_kdtree_data(pa))]
        for tpn in test_pa_node:
            for sn in son_node_knn:
                test_son_node = id_center_dict[tuple(get_kdtree_data(sn))]
                for tsn in test_son_node:
                    if tuple([tpn, tsn]) in edge_set:
                        edge_set.remove(tuple([tpn, tsn]))
                        edge_set.remove(tuple([tsn, tpn]))
                        return True
    return False


def length_metric_2(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    test_swc_list = [node for node in PreOrderIter(test_swc_tree.root())]
    id_center_dict = {}
    center_list = []
    edge_set = set()
    global dis_threshold

    for node in test_swc_list:
        if tuple(node._pos) not in id_center_dict.keys():
            id_center_dict[tuple(node._pos)] = []
        id_center_dict[tuple(node._pos)].append(node.get_id())
        center_list.append(node._pos)
        for son in node.children:
            edge_set.add(tuple([node.get_id(), son.get_id()]))
            edge_set.add(tuple([son.get_id(), node.get_id()]))

    test_kdtree = kdtree.create(center_list)
    match_lenth = 0.0

    stack = queue.LifoQueue()
    stack.put(gold_swc_tree.root())
    while not stack.empty():
        gold_node = stack.get()
        for son in gold_node.children:
            stack.put(son)

        if gold_node.is_virtual():
            continue

        gold_node_knn = test_kdtree.search_knn(gold_node._pos, K_NN)

        for node in gold_node_knn:
            if gold_node.distance(get_kdtree_data(node)) > dis_threshold:
                gold_node_knn.remove(node)
        if DEBUG:
            print("knn of gold = {}".format(gold_node_knn))
        for son in gold_node.children:
            son_node_knn = test_kdtree.search_knn(son._pos, K_NN)
            match = check_match(gold_node_knn, son_node_knn, edge_set, id_center_dict)
            if match:
                match_lenth += son.parent_distance()

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

def get_default_threshold(gold_swc_tree):
    global dis_threshold
    total_length = gold_swc_tree.length()
    total_node = gold_swc_tree.node_count()
    if total_node <= 1:
        dis_threshold = 0.1
    else:
        dis_threshold = (total_length/total_node)/10

if __name__ == "__main__":
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\ExampleGoldStandard.swc")
    get_default_threshold(goldtree)

    testTree = SwcTree()
    testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\ExampleTest.swc")
    testTree.align_roots(goldtree)
    start = time.time()
    print(length_metric_2(test_swc_tree=testTree, gold_swc_tree=goldtree,DEBUG=False))
    print(time.time() - start)