import queue
import kdtree
from anytree import PreOrderIter
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.config_utils import get_default_threshold


# for length metric (unused)
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
                        return tuple([tpn, tsn])
    return None


def create_kdtree(node_list):
    pos_node_dict = {}
    center_list = []

    for node in node_list:
        if node.is_virtual():
            continue
        pos_node_dict[node.get_center_as_tuple()] = node
        center_list.append(list(node.get_center_as_tuple()))
    my_kdtree = kdtree.create(center_list)
    return my_kdtree, pos_node_dict


def get_gold_test_dicts(gold_node_list, test_node_list):
    gold_kd, pos_gold_dict = create_kdtree(gold_node_list)
    test_kd, pos_test_dict = create_kdtree(test_node_list)

    gold_test_dict = {}
    test_gold_dict = {}

    for gold_node in gold_node_list:
        test_pos = test_kd.search_knn(list(gold_node.get_center_as_tuple()), k=1)[0]
        test_node = pos_test_dict[tuple(test_pos[0].data)]
        gold_test_dict[gold_node] = test_node
    for test_node in test_node_list:
        gold_pos = gold_kd.search_knn(list(test_node.get_center_as_tuple()), k=1)[0]
        gold_node = pos_gold_dict[tuple(gold_pos[0].data)]
        test_gold_dict[test_node] = gold_node
    return gold_test_dict, test_gold_dict


def search_knn(kdtree, id_center_dict, gold_node, knn_num):
    knn_pos = kdtree.search_knn(gold_node._pos, knn_num)
    knn_node = []
    for poses in knn_pos:
        node_list = id_center_dict[tuple(poses)]
        for node in node_list:
            knn_node.append(node)
    return knn_node[:knn_num]


def get_match_edges_p(gold_swc_tree=None, test_swc_tree=None, knn=3, DEBUG=False):
    match_edge = {}
    test_swc_list = test_swc_tree.get_node_list()

    if DEBUG:
        for item in test_swc_list:
            print("---{} {}".format(item.get_id(), item._pos))

    test_kdtree, id_center_dict, edge_set = convert_bin_to_kdtree(test_swc_list)

    stack = queue.LifoQueue()
    stack.put(gold_swc_tree.root())
    while not stack.empty():
        gold_node = stack.get()
        for son in gold_node.children:
            stack.put(son)

        if gold_node.is_virtual():
            continue

        gold_node_knn = test_kdtree.search_knn(gold_node._pos, knn)

        for node in gold_node_knn:
            if gold_node.distance(get_kdtree_data(node)) > dis_threshold:
                gold_node_knn.remove(node)
        if DEBUG:
            print("knn of gold = {}".format(gold_node_knn))
        for son in gold_node.children:
            son_node_knn = test_kdtree.search_knn(son._pos, knn)
            if DEBUG:
                print("son of gold = {}".format(son_node_knn))
            match = check_match(gold_node_knn, son_node_knn, edge_set, id_center_dict)
            if match is not None:
                match_edge[tuple([gold_node, son])] = match
    if DEBUG:
        print(len(match_edge))
    return match_edge


# for diadem metric
# def find
if __name__ == "__main__":
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\ExampleGoldStandard.swc")
    get_default_threshold(goldtree)

    testTree = SwcTree()
    testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\ExampleTest.swc")

    get_match_edges_p(goldtree, testTree, 3, True)