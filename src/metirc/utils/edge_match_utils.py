from src.model.euclidean_point import EuclideanPoint,Line
from src.metirc.utils.config_utils import dis_threshold

import numpy as np
from anytree import PreOrderIter
from rtree import index

# 获取线段的bounding box
def get_bounds(point_a, point_b):
    point_a = np.array(point_a._pos)
    point_b = np.array(point_b._pos)
    res = np.where(point_a>point_b,point_b,point_a).tolist() + np.where(point_a>point_b,point_a,point_b).tolist()
    return tuple(res)

# 获取编号到线段的映射
def get_idedge_dict(swc_tree=None):
    id_edge_dict = {}
    swc_tree_list = [node for node in PreOrderIter(swc_tree.root())]
    for node in swc_tree_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        id_edge_dict[node.get_id()] = tuple([node, node.parent])
    return id_edge_dict

# 构建rtree
def get_edge_rtree(swc_tree=None):
    swc_tree_list = [node for node in PreOrderIter(swc_tree.root())]
    p = index.Property()
    p.dimension = 3
    idx3d = index.Index(properties=p)
    for node in swc_tree_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        idx3d.insert(node.get_id(), get_bounds(node, node.parent))
    return idx3d

#基于rtree寻找距离最近的边
def get_nearest_edge(idx3d, point,id_edge_dict):
    nearest_line_id = list(idx3d.nearest(get_bounds(point,point)))[0]
    line_tuple = id_edge_dict[nearest_line_id]
    line = Line(coords=[line_tuple[0]._pos, line_tuple[1]._pos], is_segment=True)
    # print("point = {}, line_a = {}, line_b = {}".format(point._pos, line.coords[0], line.coords[1]))
    dis = point.distance(line)
    return line_tuple, dis

#根据边找匹配
def get_match_edges_e(gold_swc_tree=None, test_swc_tree=None, DEBUG=False):
    match_edge = set()
    idx3d = get_edge_rtree(test_swc_tree)
    id_edge_dict = get_idedge_dict(test_swc_tree)
    gold_node_list = [node for node in PreOrderIter(gold_swc_tree.root())]

    for node in gold_node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        e_node = EuclideanPoint(node._pos)
        e_parent = EuclideanPoint(node.parent._pos)

        line_tuple_a, dis_a = get_nearest_edge(idx3d, e_node, id_edge_dict)
        line_tuple_b, dis_b = get_nearest_edge(idx3d, e_parent, id_edge_dict)

        test_length = get_lca_length(test_swc_tree, \
                                     line_tuple_a, \
                                     line_tuple_b, \
                                     Line([e_node._pos, e_parent._pos]))
        print("test length = {} gold_length = {}".format(test_length,node.parent_distance()))
        if dis_a <= dis_threshold and dis_b <= dis_threshold:
            match_edge.add(tuple([node,node.parent]))
    return match_edge

def get_route_node(current_node, lca_id):
    res_list = []
    while not current_node.is_virtual() and not current_node.get_id() == lca_id:
        res_list.append(current_node)
        current_node = current_node.parent
    if current_node.is_virtual():
        raise Exception("[Error: ] something wrong in LCA process")
    res_list.append(current_node)
    return res_list


def get_lca_max_dis(gold_swc_tree, gold_line_a, gold_line_b, test_line):
    gold_swc_tree.get_lca_preprocess()
    lca_id = gold_swc_tree.get_lca(gold_line_a[0].get_id(), gold_line_b[0].get_id())
    route_list = []
    route_list += get_route_node(gold_line_a[0], lca_id)
    route_list += get_route_node(gold_line_b[0], lca_id)
    # root节点可能有问题
    for node in route_list:
        print(node.get_id())


def get_lca_length(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, test_line):
    point_a, point_b = test_line.get_points()
    gold_line_a = Line(coords=[gold_line_tuple_a[0]._pos, gold_line_tuple_a[1]._pos])
    gold_line_b = Line(coords=[gold_line_tuple_b[0]._pos, gold_line_tuple_b[1]._pos])

    foot_a = point_a.get_foot_point(gold_line_a)
    foot_b = point_b.get_foot_point(gold_line_b)

    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
        gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
            return foot_a.distance(foot_b)

    lca_id = gold_swc_tree.get_lca(gold_line_tuple_a[0].get_id(), gold_line_tuple_b[0].get_id())

    route_list_a = get_route_node(gold_line_tuple_a[0], lca_id)
    route_list_b = get_route_node(gold_line_tuple_b[0], lca_id)

    lca_length = 0.0
    if gold_line_tuple_a[1] in route_list_a:
        route_list_a.remove(gold_line_tuple_a[0])
        lca_length += foot_a.distance(EuclideanPoint(gold_line_tuple_a[1]._pos))
    else:
        lca_length += foot_a.distance(EuclideanPoint(gold_line_tuple_a[0]._pos))
    route_list_a.pop()
    if gold_line_tuple_b[1] in route_list_b:
        route_list_b.remove(gold_line_tuple_b[0])
        lca_length += foot_b.distance(EuclideanPoint(gold_line_tuple_b[1]._pos))
    else:
        lca_length += foot_b.distance(EuclideanPoint(gold_line_tuple_b[0]._pos))
    route_list_b.pop()

    route_list = route_list_a + route_list_b
    for node in route_list:
        lca_length += node.parent_distance()
    return lca_length