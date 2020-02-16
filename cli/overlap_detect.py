from pymets.model.swc_node import SwcNode, SwcTree, Make_Virtual
from pymets.model.euclidean_point import EuclideanPoint, Line
from pymets.metric.utils.edge_match_utils import \
    get_idedge_dict, get_edge_rtree, get_lca_length, get_nearby_edges, is_route_clean, get_route_node, DINF
from anytree import PreOrderIter
from pymets.io.save_swc import swc_save
from pymets.io.read_json import read_json
import math
import numpy as np


# make sure the match path does not contain a detected redundant edge
def is_self_root_clean(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, vis_list):
    # if two foots lay on the same edge, pass
    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
            gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
        return vis_list[gold_line_tuple_a[0].get_id()] == 1

    lca_id = gold_swc_tree.get_lca(gold_line_tuple_a[0].get_id(), gold_line_tuple_b[0].get_id())
    if lca_id is None:
        return False

    # get nodes on the route, make sure no extra node
    route_list_a = get_route_node(gold_line_tuple_a[0], lca_id)
    route_list_b = get_route_node(gold_line_tuple_b[0], lca_id)

    route_list = route_list_a + route_list_b
    for node in route_list:
        if node.get_id() == lca_id and \
                gold_line_tuple_a[0].get_id() != lca_id and \
                gold_line_tuple_b[0].get_id() != lca_id:
            continue
        if vis_list[node.get_id()] == 1:
            return False
    return True


# find successful matched edge
def get_self_match_edges_e_fast(swc_tree=None,
                                dis_threshold=None, threshold_l=None,
                                mode="not_self", DEBUG=False):
    idx3d = get_edge_rtree(swc_tree)
    id_edge_dict = get_idedge_dict(swc_tree)
    node_list = [node for node in PreOrderIter(swc_tree.root())]
    vis_list = np.zeros(len(node_list) + 10)

    for node in node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        parent = node.parent

        line_tuple_as = get_nearby_edges(idx3d, node, id_edge_dict, not_self=True)
        line_tuple_bs = get_nearby_edges(idx3d, node.parent, id_edge_dict, not_self=True)

        done = False
        for line_tuple_a_d in line_tuple_as:
            if done:
                break
            for line_tuple_b_d in line_tuple_bs:
                line_tuple_a, line_tuple_b = line_tuple_a_d[0], line_tuple_b_d[0]
                dis_a, dis_b = line_tuple_a_d[1], line_tuple_b_d[1]

                test_length = get_lca_length(swc_tree, \
                                             line_tuple_a, \
                                             line_tuple_b, \
                                             Line([node._pos, node.parent._pos]))
                gold_length = node.distance(parent)

                if dis_threshold == -1:
                    threshold1, threshold2 = node.radius(), node.parent.radius()
                else:
                    threshold1, threshold2 = dis_threshold, dis_threshold

                if threshold_l == -1:
                    threshold_tmpl = gold_length / 5
                else:
                    threshold_tmpl = threshold_l

                if dis_a <= threshold1 and dis_b <= threshold2 and \
                        math.fabs(test_length - gold_length) < threshold_tmpl:
                    if mode == "not_self" and \
                            is_self_root_clean(swc_tree, line_tuple_a, line_tuple_b, vis_list):
                        continue
                    if DEBUG:
                        print("node = {} test_length = {} gold_length = {}".format(
                            node.get_id(), test_length, gold_length
                        ))
                    node._type = 3
                    node.parent._type = 3
                    vis_list[node.get_id()] = 1
                    done = True
                    break


def overlap_detect(swc_tree, out_path, loc_config=None):
    swc_tree.get_lca_preprocess()

    dis_threshold, length_threshold = loc_config["radius_threshold"], loc_config["length_threshold"]

    get_self_match_edges_e_fast(swc_tree=swc_tree,
                                dis_threshold=dis_threshold, threshold_l=length_threshold,
                                mode="all", DEBUG=False)
    swc_save(swc_tree, out_path)


def overlap_clean(swc_tree, out_path, loc_config=None):
    swc_tree.get_lca_preprocess()

    dis_threshold, length_threshold = loc_config["radius_threshold"], loc_config["length_threshold"]

    get_self_match_edges_e_fast(swc_tree=swc_tree,
                                dis_threshold=dis_threshold, threshold_l=length_threshold,
                                mode="not_self", DEBUG=False)
    swc_save(swc_tree, out_path)


if __name__ == '__main__':
    tree = SwcTree()
    tree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\overlap\overlap_sample5.swc")

    config = read_json("D:\gitProject\mine\PyMets\config\overlap_detect.json")
    overlap_clean(tree,
                  "../output/overlap_sample5_none.swc",
                  config)
