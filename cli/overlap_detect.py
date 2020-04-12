import os

from pymets.model.swc_node import SwcNode, SwcTree, Make_Virtual
from pymets.model.euclidean_point import EuclideanPoint, Line
from pymets.metric.utils.edge_match_utils import \
    get_idedge_dict, get_edge_rtree, get_lca_length, get_nearby_edges, is_route_clean, get_route_node,\
    DINF, cal_rad_threshold, cal_len_threshold
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

        # make sure it's not a root
        if node.is_virtual() or down_pa[node].is_virtual():
            continue
        # make sure it's not continuation
        if len(node.children) != 1:
            continue

        son, pa = node.children[0], down_pa[node]
        son_dis, pa_dis, grand_dis = son.parent_distance(), node.distance(down_pa[node]), son.distance(pa)

        # make sure we are deal with a situation with high sample rate
        if son_dis > son.radius() + node.radius() or pa_dis > pa.radius() + node.radius():
            continue
        ang = get_ang(son_dis, pa_dis, grand_dis)
        if ang > ang_threshold:
            # node._type = 3
            is_active[node.get_id()] = False
            down_pa[son] = down_pa[node]
    return down_pa, is_active


def itp_ok(node=None, son=None, pa=None,
           rad_mul=1.50, center_dis=None):
    f_line = Line(e_node_1=son.get_center(), e_node_2=pa.get_center())
    e_node = node.get_center()

    foot = e_node.get_foot_point(f_line)
    if not foot.on_line(f_line):
        return False
    else:
        itp_dis = e_node.distance(foot)
        e_son = son._pos
        e_pa = pa._pos
        itp_rad = son.radius() + (pa.radius() - son.radius()) * e_son.distance(foot) / e_son.distance(e_pa)
        if center_dis is None:
            center_dis = node.radius()/2
        if node.radius() / itp_rad > rad_mul or itp_dis > center_dis:
            return False

    return True


def down_sample_itp(swc_tree=None, tree_size=None, rad_mul=1.50, center_dis=None, stage=0):
    stack = queue.LifoQueue()
    stack.put(swc_tree.root())
    down_pa = {}
    is_active = [True]*(tree_size + 5)

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
        if stage == 0 and (son_dis > son.radius() + node.radius() or pa_dis > pa.radius() + node.radius()):
            continue
        if stage == 1 and (son_dis > son.radius() + node.radius() and pa_dis > pa.radius() + node.radius()):
            continue
        if itp_ok(node=node, son=son, pa=pa, rad_mul=rad_mul, center_dis=center_dis):
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
            node.parent.remove_child(node)
    swc_tree.node_list = [node for node in PreOrderIter(swc_tree.root())]


def overlap_detect(swc_tree, out_path, loc_config=None):
    swc_tree.get_lca_preprocess()

    rad_threshold, len_threshold = loc_config["radius_threshold"], loc_config["length_threshold"]
    down_pa, is_active = down_sample(tree, 170)

    get_self_match_edges_e_fast(swc_tree=swc_tree,
                                rad_threshold=rad_threshold, len_threshold=len_threshold,
                                mode="all", DEBUG=False)
    swc_save(swc_tree, out_path)


def overlap_clean(swc_tree, out_path, loc_config=None):
    dis_threshold, length_threshold, ang_threshold = \
        loc_config["radius_threshold"], loc_config["length_threshold"], loc_config["ang_threshold"]
    # down_pa, is_active = down_sample(tree, 170)
    down_pa, is_active = down_sample_itp(swc_tree=tree, tree_size=swc_tree.node_count(), stage=0)
    new_swc_tree = reconstruct_tree(swc_tree, is_active, down_pa)
    down_pa, is_active = down_sample_itp(swc_tree=new_swc_tree, tree_size=swc_tree.node_count(), stage=1)
    new_swc_tree = reconstruct_tree(new_swc_tree, is_active, down_pa)

    new_swc_tree.get_lca_preprocess(swc_tree.node_count())
    swc_tree.get_lca_preprocess(swc_tree.node_count())

    get_self_match_edges_e_fast(swc_tree=new_swc_tree,
                                rad_threshold=dis_threshold,
                                len_threshold=length_threshold,
                                list_size=swc_tree.node_count(),
                                mode="not_self", DEBUG=False)
    color_origin_tree(new_swc_tree, swc_tree)
    delete_overlap_node(new_swc_tree)
    swc_save(new_swc_tree, out_path)


if __name__ == '__main__':
    file_path = "D:\gitProject\mine\PyMets\\test\data_example\gold\swc_data_2"
    out_path = "D:\gitProject\mine\PyMets\output\swc_data_2"

    files = os.listdir(file_path)
    for file in files:
        tree = SwcTree()
        tree.clear()
        tree.load(os.path.join(file_path, file))

        config = read_json("D:\gitProject\mine\PyMets\config\overlap_detect.json")
        overlap_clean(tree,
                      os.path.join(out_path, "clean_"+file),
                      config)

    # node = SwcNode(center=[101, 100.1, 100], radius=0.6)
    # son = SwcNode(center=[100, 100, 100], radius=0.5)
    # pa = SwcNode(center=[102, 100, 100], radius=0.5)
    # print(itp_ok(node=node, son=son, pa=pa))
