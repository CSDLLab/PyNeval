import os

from pyneval.model.swc_node import SwcTree
from pyneval.model.euclidean_point import Line
from pyneval.metric.utils.edge_match_utils import \
    get_idedge_dict, get_edge_rtree, get_lca_length, get_nearby_edges, get_route_node, \
    cal_rad_threshold, cal_len_threshold
from pyneval.tools.re_sample import down_sample_swc_tree_command_line
from anytree import PreOrderIter
from pyneval.io.save_swc import swc_save
from pyneval.io.read_json import read_json
import math
import numpy as np


# make sure the match path does not contain a detected redundant edge
def is_self_root_clean(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, vis_list):
    # if two foots lay on the same edge, pass
    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
            gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
        return vis_list[gold_line_tuple_a[0].get_id()] != 1

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


def get_ang(side_edge1, side_edge2, oppo_edge):
    c = (side_edge1**2 + side_edge2**2 - oppo_edge**2) / (2 * side_edge1 * side_edge2)
    c = round(c, 4)
    if not (-1.0 <= c <= 1.0):
        raise Exception("[Error: ]In file overlap_detect.py, input is not a legal triangle {} {} {}".format(
            side_edge1, side_edge2, oppo_edge
        ))
    return math.acos(c) * 180 / math.pi


def color_origin_tree(new_swc_tree, swc_tree):
    new_swc_list = [node for node in PreOrderIter(new_swc_tree.root())]
    id_node_map = {}

    for node in PreOrderIter(swc_tree.root()):
        id_node_map[node.get_id()] = node

    for node in new_swc_list:
        if node._type == 3:
            o_node = id_node_map[node.get_id()]
            while o_node.get_id() != node.parent.get_id():
                o_node._type = 3
                o_node = o_node.parent


# find overlap edges
def get_self_match_edges_e_fast(swc_tree=None,
                                rad_threshold=None, len_threshold=None, list_size=-1,
                                mode="not_self", DEBUG=False):
    idx3d = get_edge_rtree(swc_tree)
    id_edge_dict = get_idedge_dict(swc_tree)
    # sort the tree according the tree size
    roots = swc_tree.root().children
    id_rootdis_dict = {}
    node_list = []
    root_list = []
    for root in roots:
        r_list = [node for node in PreOrderIter(root)]
        root_list.append(tuple([root, len(r_list)]))
    root_list.sort(key=lambda x: x[1])

    for root in root_list:
        r_list = [node for node in PreOrderIter(root[0])]
        node_list += r_list

    if list_size == -1:
        list_size = len(node_list)

    for node in node_list:
        id_rootdis_dict[node.get_id()] = node.root_length

    vis_list = np.zeros(list_size + 10)
    for node in node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        parent = node.parent

        rad_threshold1, rad_threshold2 = cal_rad_threshold(rad_threshold, node.radius(), node.parent.radius())

        line_tuple_as = get_nearby_edges(idx3d, node, id_edge_dict, threshold=rad_threshold1, not_self=True)
        line_tuple_bs = get_nearby_edges(idx3d, parent, id_edge_dict, threshold=rad_threshold2, not_self=True)

        done = False
        for line_tuple_a_d in line_tuple_as:
            if done:
                break
            for line_tuple_b_d in line_tuple_bs:
                line_tuple_a, line_tuple_b = line_tuple_a_d[0], line_tuple_b_d[0]
                dis_a, dis_b = line_tuple_a_d[1], line_tuple_b_d[1]

                test_length = get_lca_length(swc_tree,
                                             line_tuple_a,
                                             line_tuple_b,
                                             Line(e_node_1=node.get_center(),
                                                  e_node_2=node.parent.get_center()),
                                             id_rootdis_dict)
                gold_length = node.distance(parent)
                len_threshold1 = cal_len_threshold(len_threshold, gold_length)

                if dis_a <= rad_threshold1 and dis_b <= rad_threshold2 and \
                        math.fabs(test_length - gold_length) < len_threshold1:
                    if mode == "not_self" and not is_self_root_clean(swc_tree, line_tuple_a, line_tuple_b, vis_list):
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


def delete_overlap_node(swc_tree):
    node_list = swc_tree.get_node_list()
    for node in node_list:
        if node._type == 3:
            for son in node.children:
                son.parent = swc_tree.root()
            swc_tree.remove_child(node.parent, node)
    swc_tree.node_list = [node for node in PreOrderIter(swc_tree.root())]


def overlap_clean(swc_tree, out_path, file_name, loc_config=None):
    '''
    :param swc_tree: input swc tree
    :param out_path: output fold path
    :param file_name: name your file as you want
    :param loc_config:  load config/overlap_clean.json
    :return:
    '''
    dis_threshold, length_threshold, ang_threshold = \
        loc_config["radius_threshold"], loc_config["length_threshold"], loc_config["ang_threshold"]

    new_swc_tree = down_sample_swc_tree_command_line(swc_tree, loc_config)
    new_swc_tree = down_sample_swc_tree_command_line(new_swc_tree, loc_config)

    new_swc_tree.get_lca_preprocess(swc_tree.size())
    swc_tree.get_lca_preprocess(swc_tree.size())

    get_self_match_edges_e_fast(swc_tree=new_swc_tree,
                                rad_threshold=dis_threshold,
                                len_threshold=length_threshold,
                                list_size=swc_tree.size(),
                                mode="not_self", DEBUG=False)
    color_origin_tree(new_swc_tree, swc_tree)
    swc_save(new_swc_tree, os.path.join(out_path, os.path.join('marked_data', file_name)))
    delete_overlap_node(new_swc_tree)
    swc_save(new_swc_tree, os.path.join(out_path, os.path.join('clean_data', file_name)))


if __name__ == '__main__':
    file_path = "D:\gitProject\mine\PyNeval\\test\data_example\gold\swc_18254_1"
    out_path = "D:\gitProject\mine\PyNeval\output\swc_18254_1"

    files = os.listdir(file_path)
    for file in files:
        tree = SwcTree()
        tree.clear()
        tree.load(os.path.join(file_path, file))

        config = read_json("D:\gitProject\mine\PyNeval\config\overlap_clean.json")
        overlap_clean(tree, out_path, file, config)

