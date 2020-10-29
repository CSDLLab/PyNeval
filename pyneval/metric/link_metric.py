import sys
import time

from pyneval.metric.utils.config_utils import DINF
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.km_utils import KM, get_dis_graph
from pyneval.io.read_json import read_json
from pyneval.metric.utils.point_match_utils import get_swc2swc_dicts

def get_neighbors(node):
    neighbors = list(node.children)
    if node.parent is not None and not node.parent.is_virtual():
        neighbors.append(node.parent)
    return neighbors


def get_same_pos_nodes(gold_nodes, test_nodes):
    res = []
    for gold_node in gold_nodes:
        for test_node in test_nodes:
            if gold_node.get_center_as_tuple() == test_node.get_center_as_tuple():
                res.append(gold_node)
                break
    return res


def get_extra_pos_nodes(big_set, subset):
    res = []
    pos_set = set()
    for node in subset:
        pos_set.add(node.get_center_as_tuple())

    for node in big_set:
        if not node.get_center_as_tuple() in pos_set:
            res.append(node)
    return res


def link_metric(gold_swc_tree, test_swc_tree, config):
    gold_list = gold_swc_tree.get_node_list()
    test_list = test_swc_tree.get_node_list()

    gold_test_dict = get_swc2swc_dicts(src_node_list=gold_swc_tree.get_node_list(),
                                       tar_node_list=test_swc_tree.get_node_list())
    test_gold_dict = get_swc2swc_dicts(src_node_list=test_swc_tree.get_node_list(),
                                       tar_node_list=gold_swc_tree.get_node_list())

    edge_loss, tree_dis_loss = 0.0, 0.0
    for gold_node in gold_list:
        if gold_node.is_virtual():
            continue

        test_node = gold_test_dict[gold_node]

        # attention: nodes in test neighbors are labeled by TEST tree label
        test_neighbors = get_neighbors(test_node)
        gold_neighbors = get_neighbors(gold_node)

        nodes_in_same_pos = get_same_pos_nodes(gold_neighbors, test_neighbors)
        nodes_gold_extra = get_extra_pos_nodes(gold_neighbors, nodes_in_same_pos)
        # attention: nodes in test neighbors are labeled by TEST tree label
        nodes_test_extra = get_extra_pos_nodes(test_neighbors, nodes_in_same_pos)

        for gold_extra in nodes_gold_extra:
            edge_loss += gold_extra.distance(gold_node)

        for test_extra in nodes_test_extra:
            map_test_extra = test_gold_dict[test_extra]
            edge_loss += map_test_extra.distance(gold_node)

        # if two nodes are not connected, the dis will be set as DINF, so the threshold need to be set as DINF - 1
        dis_graph, switch, test_len, gold_len = \
            get_dis_graph(gold_tree=gold_swc_tree, test_tree=test_swc_tree,
                          gold_node_list=nodes_gold_extra, test_node_list=nodes_test_extra,
                          test_gold_dict=test_gold_dict, threshold_dis=DINF-1, mode=2)

        km = KM(maxn=max(test_len, gold_len) + 10, nx=test_len, ny=gold_len, G=dis_graph)
        km.solve()
        tree_dis_loss += -km.get_max_dis()

    return edge_loss, tree_dis_loss


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    start = time.time()
    gold_swc_tree = SwcTree()
    test_swc_tree = SwcTree()
    test_swc_tree.load("..\\..\\data\\branch_metric_data\\test\\194444.swc")
    gold_swc_tree.load("..\\..\\data\\branch_metric_data\\gold\\194444.swc")
    config = read_json("..\\..\\config\\branch_metric.json")
    edge_loss, tree_dis_loss = link_metric(test_swc_tree=test_swc_tree, gold_swc_tree=gold_swc_tree, config=config)
    print(edge_loss, tree_dis_loss)
