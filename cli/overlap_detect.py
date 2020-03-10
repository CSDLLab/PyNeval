from pymets.model.swc_node import SwcNode, SwcTree, Make_Virtual
from pymets.model.euclidean_point import EuclideanPoint, Line
from pymets.metric.utils.edge_match_utils import \
    get_idedge_dict, get_edge_rtree, get_lca_length, get_nearby_edges, is_route_clean, get_route_node, DINF
from anytree import PreOrderIter
from pymets.io.save_swc import swc_save
from pymets.io.read_json import read_json
import math,queue
import numpy as np
import copy
import time

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


def down_sample(swc_tree=None, ang_threshold=175):
    stack = queue.LifoQueue()
    stack.put(swc_tree.root())
    down_pa = {}
    is_active = [True]*(swc_tree.node_count() + 5)

    for node in PreOrderIter(swc_tree.root()):
        if node.parent is None or node is None:
            continue
        down_pa[node] = node.parent

    while not stack.empty():
        node = stack.get()
        for son in node.children:
            stack.put(son)

        # 确保不是根节点
        if node.is_virtual() or down_pa[node].is_virtual():
            continue
        # 确保是二度节点
        if len(node.children) != 1:
            continue

        son, pa = node.children[0], down_pa[node]
        son_dis, pa_dis, grand_dis = son.parent_distance(), node.distance(down_pa[node]), son.distance(pa)

        # 确保针对采样率高的情况
        if son_dis > son.radius() + node.radius() and pa_dis > pa.radius() + node.radius():
            continue
        ang = get_ang(son_dis, pa_dis, grand_dis)
        if ang > ang_threshold:
            # node._type = 3
            is_active[node.get_id()] = False
            down_pa[son] = down_pa[node]
    return down_pa, is_active


def reconstruct_tree(swc_tree, is_activate, down_pa):
    new_swc_tree = SwcTree()
    node_list = [node for node in PreOrderIter(swc_tree.root())]
    id_node_map = {-1: new_swc_tree.root()}

    for node in node_list:
        if node.is_virtual():
            continue
        if is_activate[node.get_id()]:
            tmp_node = SwcNode()
            tmp_node._id = node.get_id()
            tmp_node._type = node._type
            tmp_node._pos = copy.copy(node._pos)
            tmp_node._radius = node._radius
            pa = id_node_map[down_pa[node].get_id()]
            tmp_node.parent = pa
            id_node_map[node.get_id()] = tmp_node
    return new_swc_tree


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
                                dis_threshold=None, threshold_l=None, list_size = -1,
                                mode="not_self", DEBUG=False):
    idx3d = get_edge_rtree(swc_tree)
    id_edge_dict = get_idedge_dict(swc_tree)
    # sort the tree according the tree size
    roots = swc_tree.root().children
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

    vis_list = np.zeros(list_size + 10)
    for node in node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        parent = node.parent

        line_tuple_as = get_nearby_edges(idx3d, node, id_edge_dict, not_self=True)
        line_tuple_bs = get_nearby_edges(idx3d, parent, id_edge_dict, not_self=True)

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
                                             Line([node._pos, parent._pos]))
                gold_length = node.distance(parent)

                if dis_threshold == -1:
                    threshold1, threshold2 = node.radius(), parent.radius()
                else:
                    threshold1, threshold2 = dis_threshold, dis_threshold

                if threshold_l == -1:
                    threshold_tmpl = gold_length / 5
                else:
                    threshold_tmpl = threshold_l

                if dis_a <= threshold1 and dis_b <= threshold2 and \
                        math.fabs(test_length - gold_length) < threshold_tmpl:
                    if mode == "not_self" and not is_self_root_clean(swc_tree, line_tuple_a, line_tuple_b, vis_list):
                        continue
                    if DEBUG:
                        print("node = {} test_length = {} gold_length = {}".format(
                            node.get_id(), test_length, gold_length
                        ))
                    node._type = 3
                    # node.parent._type = 3
                    vis_list[node.get_id()] = 1
                    done = True
                    break


def delete_overlap_node(swc_tree):
    node_list = [node for node in PreOrderIter(swc_tree.root())]
    for node in node_list:
        if node._type == 3:
            for son in node.children:
                son.parent = node_list[0]
            node.parent.remove_child(node)


def overlap_detect(swc_tree, out_path, loc_config=None):
    swc_tree.get_lca_preprocess()

    dis_threshold, length_threshold = loc_config["radius_threshold"], loc_config["length_threshold"]
    down_pa, is_active = down_sample(tree, 170)

    get_self_match_edges_e_fast(swc_tree=swc_tree,
                                dis_threshold=dis_threshold, threshold_l=length_threshold,
                                mode="all", DEBUG=False)
    swc_save(swc_tree, out_path)


def overlap_clean(swc_tree, out_path, loc_config=None):
    dis_threshold, length_threshold, ang_threshold = \
        loc_config["radius_threshold"], loc_config["length_threshold"], loc_config["ang_threshold"]
    down_pa, is_active = down_sample(tree, 170)
    new_swc_tree = reconstruct_tree(swc_tree, is_active, down_pa)
    new_swc_tree.get_lca_preprocess(swc_tree.node_count())
    swc_tree.get_lca_preprocess(swc_tree.node_count())

    get_self_match_edges_e_fast(swc_tree=swc_tree,
                                dis_threshold=dis_threshold,
                                threshold_l=length_threshold,
                                list_size=swc_tree.node_count(),
                                mode="not_self", DEBUG=False)
    color_origin_tree(new_swc_tree, swc_tree)
    # delete_overlap_node(swc_tree)
    swc_save(swc_tree, out_path)


if __name__ == '__main__':
    tree = SwcTree()
    tree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\overlap\\branches3_screen.swc")

    config = read_json("D:\gitProject\mine\PyMets\config\overlap_detect.json")
    overlap_clean(tree,
                  "../output/branches3_screen.swc",
                  config)
