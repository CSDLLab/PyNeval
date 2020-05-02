from pyneval.model.euclidean_point import EuclideanPoint,Line
from pyneval.metric.utils.config_utils import DINF
import time
from anytree import PreOrderIter
from pyneval.model.swc_node import SwcTree

MIN_SIZE = 0.8


def get_nearest_edge(gold_node, test_edge_list, DEBUG=False):
    dis = DINF
    match_line = None
    for test_edge in test_edge_list:
        test_line = Line(swc_node_1=test_edge[0],swc_node_2=test_edge[1])
        eu_node = EuclideanPoint(gold_node._pos)
        tmp_dis = eu_node.distance(test_line)
        tmp_line = test_edge

        if DEBUG:
            eu_node.to_str()
            test_line.to_str()
            print("tmp_dis = {}".format(tmp_dis))

        if tmp_dis < dis:
            dis = tmp_dis
            match_line = tmp_line

    return match_line, dis


def get_test_edge_list(node_list):
    edge_list = []
    for node in node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        edge_list.append(tuple([node, node.parent]))
    return edge_list


#根据边找匹配
def get_match_edges_e(gold_swc_tree=None, test_swc_tree=None, dis_threshold=0.1, DEBUG=False):
    match_edge = set()
    gold_node_list = [node for node in PreOrderIter(gold_swc_tree.root())]
    test_node_list = [node for node in PreOrderIter(test_swc_tree.root())]
    test_edge_list = get_test_edge_list(test_node_list)

    for node in gold_node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        e_node = EuclideanPoint(node._pos)
        e_parent = EuclideanPoint(node.parent._pos)

        line_tuple_a, dis_a = get_nearest_edge(e_node, test_edge_list, DEBUG=False)
        line_tuple_b, dis_b = get_nearest_edge(e_parent, test_edge_list, DEBUG=False)
        if dis_a <= dis_threshold and dis_b <= dis_threshold:
            match_edge.add(tuple([node, node.parent]))
            if DEBUG:
                with open('normal.txt', 'a') as f:
                    f.write("\nnode = {} {}\nnode.parent = {} {}\nnode_line = {},{}\nnode_p_line = {},{}\n".format(
                        node.get_id(), node._pos,
                        node.parent.get_id(),node.parent._pos,
                        line_tuple_a[0]._pos, line_tuple_a[1]._pos,
                        line_tuple_b[0]._pos, line_tuple_b[1]._pos,
                    ))
    return match_edge


def length_metric_2_2(gold_swc_tree=None, test_swc_tree=None, dis_threshold=0.1, DEBUG=False):
    match_edges = get_match_edges_e(gold_swc_tree, test_swc_tree,dis_threshold, DEBUG=True)

    match_length = 0.0
    for line_tuple in match_edges:
        match_length += line_tuple[0].parent_distance()

    gold_total_length = round(gold_swc_tree.length(),8)
    match_length = round(match_length,8)

    if DEBUG:
        print("match_length b = {}, gold_total_length = {}"
              .format(match_length, gold_total_length))
    return match_length/gold_total_length

if __name__ == "__main__":
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\30_18_10_gold.swc")

    testTree = SwcTree()
    testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\30_18_10_test.swc")
    start = time.time()
    print(length_metric_2_2(gold_swc_tree=goldtree,
                        test_swc_tree=testTree))

    print(time.time() - start)