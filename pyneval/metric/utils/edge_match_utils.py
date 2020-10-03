from pyneval.model.euclidean_point import EuclideanPoint,Line
from pyneval.metric.utils.config_utils import DINF
from pyneval.model.swc_node import get_lca, SwcNode
from pyneval.io.save_swc import swc_save

import numpy as np
import math, copy
from anytree import PreOrderIter
from rtree import index

MIN_SIZE = 0.8
FLOAT_ERROR = 0.001


# public
# find successful matched edge
def get_match_edges(gold_swc_tree=None, test_swc_tree=None,
                    vertical_tree=None,
                    rad_threshold=-1.0, len_threshold=0.2,
                    detail_path=None, DEBUG=False):
    """
    :param gold_swc_tree: Swc_Tree
    :param test_swc_tree: Swc_Tree
    :param vertical_tree: swc format string list, initially empty tree, store vertical edge between two trees
    :param rad_threshold: float, radius threshold
    :param len_threshold: float, length threshold
    :param detail_path: string, path for extra detail
    :param DEBUG: bool, true or false, to show DEBUG info or not
    :return: match_edge set contains tuple of two swc nodes
    level: 0
    """

    match_edge = set()
    edge_use_dict = {}
    id_rootdis_dict = {}
    test_match_length = 0.0
    vertical_id = 1
    idx3d = get_edge_rtree(test_swc_tree)
    id_edge_dict = get_idedge_dict(test_swc_tree)
    gold_node_list = gold_swc_tree.get_node_list()
    test_node_list = test_swc_tree.get_node_list()

    # node num need to be larger than the max id
    test_maxum = 0
    for node in test_node_list:
        id_rootdis_dict[node.get_id()] = node.root_length
        test_maxum = max(test_maxum, node.get_id())

    vis_list = np.zeros(test_maxum+5, dtype='int8')
    test_swc_tree.get_lca_preprocess(node_num=test_maxum+5)

    for node in gold_node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        rad_threshold1, rad_threshold2 = cal_rad_threshold(rad_threshold, node.radius(), node.parent.radius())

        line_tuple_a_set = get_nearby_edges(idx3d=idx3d, point=node, id_edge_dict=id_edge_dict,
                                            threshold=rad_threshold1, not_self=False, DEBUG=False)
        line_tuple_b_set = get_nearby_edges(idx3d=idx3d, point=node.parent, id_edge_dict=id_edge_dict,
                                            threshold=rad_threshold2, not_self=False, DEBUG=False)

        done = False
        for line_tuple_a_dis in line_tuple_a_set:
            if done:
                break
            for line_tuple_b_dis in line_tuple_b_set:
                line_tuple_a = line_tuple_a_dis[0]
                dis_a = line_tuple_a_dis[1]
                line_tuple_b = line_tuple_b_dis[0]
                dis_b = line_tuple_b_dis[1]

                test_length = get_lca_length(test_swc_tree, \
                               line_tuple_a, \
                               line_tuple_b, \
                               Line(e_node_1=node.get_center(),
                                    e_node_2=node.parent.get_center()),
                               id_rootdis_dict)
                gold_length = node.parent_distance()

                if test_length == DINF:
                    continue

                len_threshold1 = cal_len_threshold(len_threshold, gold_length)
                if not (dis_a <= rad_threshold1 and dis_b <= rad_threshold2):
                    # print(node.get_id(), dis_a, rad_threshold1, dis_b, rad_threshold2, "error1")
                    continue
                if not (math.fabs(test_length - gold_length) < len_threshold1):
                    # print(node.get_id(), "error2")
                    continue
                if not is_route_clean(gold_swc_tree=test_swc_tree,
                                      gold_line_tuple_a=line_tuple_a, gold_line_tuple_b=line_tuple_b,
                                      node1=node, node2=node.parent,
                                      edge_use_dict=edge_use_dict, vis_list= vis_list, DEBUG=False):
                    # print(node.get_id(), "error3")
                    continue
                match_edge.add(tuple([node, node.parent]))
                vertical_id = adjust_vertical_tree(node, line_tuple_a, line_tuple_b, vertical_tree, vertical_id)
                test_match_length += test_length
                done = True
                break

        if not done:
            node._type = 6
            # print("{} not done".format(node.get_id()))
            # node.parent._type = 6
    # debugging
    swc_save(gold_swc_tree, "..\..\output\out_30_18_10.swc")
    return match_edge, test_match_length


def adjust_vertical_tree(node, line_tuple_a, line_tuple_b, vertical_tree, vertical_id):
    # adjust vertical tree
    swc_foot_a = swc_get_foot(node, line_tuple_a)
    swc_foot_b = swc_get_foot(node.parent, line_tuple_b)
    tmp_node = SwcNode(center=node._pos, radius=node.radius() / 2, ntype=node._type)
    tmp_node_p = SwcNode(center=node.parent._pos, radius=node.parent.radius() / 2, ntype=node.parent._type)

    tmp_node.set_id(vertical_id)
    vertical_id += 1
    vertical_tree.append(tmp_node.to_swc_str(-1))

    tmp_node_p.set_id(vertical_id)
    vertical_id += 1
    vertical_tree.append(tmp_node_p.to_swc_str(-1))

    swc_foot_a.set_id(vertical_id)
    vertical_id += 1
    vertical_tree.append(swc_foot_a.to_swc_str(tmp_node.get_id()))

    swc_foot_b.set_id(vertical_id)
    vertical_id += 1
    vertical_tree.append(swc_foot_b.to_swc_str(tmp_node_p.get_id()))
    return vertical_id


# private
# construct rtree
def get_edge_rtree(swc_tree=None):
    """
    :param swc_tree: Swc_Tree, to build rtree
    :return: rtree
    level: 1
    """
    swc_tree_list = swc_tree.get_node_list()
    p = index.Property()
    p.dimension = 3
    idx3d = index.Index(properties=p)
    for node in swc_tree_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        idx3d.insert(node.get_id(), get_bounds(node, node.parent, extra=node.radius()))
    return idx3d


# get bounding box of a segment
def get_bounds(point_a, point_b, extra = 0):
    """
    :param point_a: two points to identify the square
    :param point_b:
    :param extra: float, a threshold
    :return:
    """
    point_a = np.array(point_a.get_center()._pos)
    point_b = np.array(point_b.get_center()._pos)
    res = (np.where(point_a > point_b, point_b, point_a) - extra).tolist() + (np.where(point_a > point_b, point_a, point_b) + extra).tolist()

    return tuple(res)


# get a dict, id_edge_dict[id] = tuple(swc_node1, swc_node2)
def get_idedge_dict(swc_tree=None):
    '''
    :param swc_tree:
    :return:Dict
    get a dict mapping id and edge on the swc tree.
    level:1
    '''
    id_edge_dict = {}
    swc_tree_list = swc_tree.get_node_list()
    for node in swc_tree_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        id_edge_dict[node.get_id()] = tuple([node, node.parent])
    return id_edge_dict


def cal_rad_threshold(rad_threshold, dis1, dis2):
    if rad_threshold < 0:
        return -rad_threshold*dis1, -rad_threshold*dis2
    else:
        return rad_threshold, rad_threshold


def cal_len_threshold(len_threshold, length):
    return length * len_threshold


def get_nearby_edges_slow(test_node_list, point, threshold, not_self=False, DEBUG=False):
    nearby_edges = []
    for node in test_node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        e_point = point.get_center()

        new_d = e_point.distance(Line(e_node_1=node.get_center(), e_node_2=node.parent.get_center()))
        if not_self and new_d == 0:
            continue
        if new_d < threshold:
            line_tuple = ([node, node.parent])
            nearby_edges.append(tuple([line_tuple, new_d]))
    nearby_edges.sort(key=lambda x: x[1])
    return nearby_edges


# find the closest edge base on rtree
def get_nearby_edges(idx3d, point, id_edge_dict, threshold, not_self=False, DEBUG=False):
    '''
    :param idx3d: an rtree
    :param point: point to get nearby edges
    :param id_edge_dict:map between id and line tuple(edge)
    :param threshold:
    :param not_self: exclude self,used in overlap detect
    :param DEBUG:
    :return: a list of tuple(edge, dis). Sorted according to dis
    level: 1
    '''
    point_box = (point.get_x() - threshold, point.get_y() - threshold, point.get_z() - threshold,
                 point.get_x() + threshold, point.get_y() + threshold, point.get_z() + threshold)
    hits = list(idx3d.intersection(point_box))
    nearby_edges = []

    for h in hits:
        line_tuple = id_edge_dict[h]
        if DEBUG:
            print("\npoint = id{} poi{}, line_a = id{} poi{}, line_b = id{} poi{}".format(
                point.get_id(), point.get_center()._pos,
                line_tuple[0].get_id(), line_tuple[0].get_center()._pos,
                line_tuple[1].get_id(), line_tuple[1].get_center()._pos)
            )
        e_point = point.get_center()

        # if two sides of line_tuple is in the same position, ignore this line
        if line_tuple[0].get_center().distance(line_tuple[1].get_center()) == 0:
            continue

        new_d = e_point.distance(Line(e_node_1=line_tuple[0].get_center(), e_node_2=line_tuple[1].get_center()))
        if not_self and new_d == 0:
            continue
        nearby_edges.append(tuple([line_tuple, new_d]))
    nearby_edges.sort(key=lambda x: x[1])
    return nearby_edges


# get the distance of two matched closest edges
def get_lca_length(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, test_line, id_rootdis_dict):
    '''
    level: 1
    '''
    point_a, point_b = test_line.get_points()

    gold_line_a = Line(e_node_1=gold_line_tuple_a[0].get_center(),
                       e_node_2=gold_line_tuple_a[1].get_center())
    gold_line_b = Line(e_node_1=gold_line_tuple_b[0].get_center(),
                       e_node_2=gold_line_tuple_b[1].get_center())

    foot_a = point_a.get_closest_point(gold_line_a)
    foot_b = point_b.get_closest_point(gold_line_b)

    # if two foots lay on the same edge, pass
    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
        gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
        return foot_a.distance(foot_b)

    lca_id = gold_swc_tree.get_lca(gold_line_tuple_a[0].get_id(), gold_line_tuple_b[0].get_id())
    if lca_id is None or lca_id < 1:
        return DINF
    try:
        lca_length2 = id_rootdis_dict[gold_line_tuple_a[0].get_id()] + \
                      id_rootdis_dict[gold_line_tuple_b[0].get_id()] - \
                      id_rootdis_dict[lca_id]*2
    except:
        print(id_rootdis_dict)
        raise Exception("[error: lca_id={}]".format(
            lca_id
        ))
    # get nodes on the route, make sure no extra node
    route_list_a = get_route_node(gold_line_tuple_a[0], lca_id)
    route_list_b = get_route_node(gold_line_tuple_b[0], lca_id)

    lca_length = 0.0
    # if (gold_line_tuple_a[1] in route_list_a) != (gold_line_tuple_a[0].get_id() != lca_id):
    #     print(gold_line_tuple_a[1] in route_list_a, gold_line_tuple_a[0].get_id() != lca_id)
    if gold_line_tuple_a[0].get_id() != lca_id:
        route_list_a.remove(gold_line_tuple_a[0])
        lca_length2 -= gold_line_tuple_a[0].parent_distance()
        lca_length += foot_a.distance(gold_line_tuple_a[1].get_center())
        lca_length2 += foot_a.distance(gold_line_tuple_a[1].get_center())
    else:
        lca_length += foot_a.distance(gold_line_tuple_a[0].get_center())
        lca_length2 += foot_a.distance(gold_line_tuple_a[0].get_center())
    # if (gold_line_tuple_b[1] in route_list_b) != (gold_line_tuple_b[0].get_id() != lca_id):
    #     print(gold_line_tuple_b[1] in route_list_b, gold_line_tuple_b[0].get_id() != lca_id)
    if gold_line_tuple_b[0].get_id() != lca_id:
        route_list_b.remove(gold_line_tuple_b[0])
        lca_length2 -= gold_line_tuple_b[0].parent_distance()
        lca_length += foot_b.distance(gold_line_tuple_b[1].get_center())
        lca_length2 += foot_b.distance(gold_line_tuple_b[1].get_center())
    else:
        lca_length += foot_b.distance(gold_line_tuple_b[0].get_center())
        lca_length2 += foot_b.distance(gold_line_tuple_b[0].get_center())

    route_list = route_list_a + route_list_b
    for node in route_list:
        if node.get_id() == lca_id:
            continue
        lca_length += node.parent_distance()
    # if lca_length-lca_length2 > 0.0000001:
    #     print(lca_length, lca_length2)
    return lca_length


#
def is_route_clean(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, node1, node2, edge_use_dict, vis_list, DEBUG):
    '''
    level: 1
    check if any part between two pedals is used
    '''
    point_a = node1.get_center()
    point_b = node2.get_center()
    gold_line_a = Line(e_node_1=gold_line_tuple_a[0].get_center(), e_node_2=gold_line_tuple_a[1].get_center())
    gold_line_b = Line(e_node_1=gold_line_tuple_b[0].get_center(), e_node_2=gold_line_tuple_b[1].get_center())

    foot_a = point_a.get_closest_point(gold_line_a)
    foot_b = point_b.get_closest_point(gold_line_b)

    # if two foots lay on the same edge, pass
    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
        gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
            total_length = gold_line_tuple_a[0].distance(gold_line_tuple_a[1])
            start = foot_a.distance(gold_line_tuple_a[0].get_center()) / total_length
            end = foot_b.distance(gold_line_tuple_a[0].get_center()) / total_length
            if DEBUG:
                print("node = {} {}\nnode.parent = {} {}\nnode_line = {},{} usage = {} {}\n".format(
                        node1.get_id(), node1.get_center()._pos,
                        node2.get_id(), node2.get_center()._pos,
                        gold_line_tuple_a[0].get_id(), gold_line_tuple_a[1].get_id(), start, end,
                    ))
            if start > end:
                start, end = end, start
            end -= FLOAT_ERROR
            if vis_list[gold_line_tuple_a[0].get_id()] == 1:
                return False
            if add_interval(edge_use_dict, gold_line_tuple_a[0], tuple([start, end])):
                if start < end:
                    edge_use_dict[gold_line_tuple_a[0]].add(tuple([start, end]))
                return True
            return False

    # not on the same edge, get lca first
    lca_id = gold_swc_tree.get_lca(gold_line_tuple_a[0].get_id(), gold_line_tuple_b[0].get_id())
    if lca_id is None:
        raise Exception("[Error:] No Lca found")

    # get nodes on the route, make sure no extra node
    route_list_a = get_route_node(gold_line_tuple_a[0], lca_id)
    route_list_b = get_route_node(gold_line_tuple_b[0], lca_id)

    if gold_line_tuple_a[1] in route_list_a:
        route_list_a.remove(gold_line_tuple_a[0])
        start_a = foot_a.distance(gold_line_tuple_a[0].get_center()) / gold_line_tuple_a[0].parent_distance()
        end_a = 1.0
    else:
        start_a = 0.0
        end_a = foot_a.distance(gold_line_tuple_a[0].get_center()) / gold_line_tuple_a[0].parent_distance()

    if gold_line_tuple_b[1] in route_list_b:
        route_list_b.remove(gold_line_tuple_b[0])
        start_b = foot_b.distance(gold_line_tuple_b[0].get_center()) / gold_line_tuple_b[0].parent_distance()
        end_b = 1.0
    else:
        start_b = 0.0
        end_b = foot_b.distance(gold_line_tuple_b[0].get_center()) / gold_line_tuple_b[0].parent_distance()

    if DEBUG:
        print("\nnode = {} {}\nnode.parent = {} {}\nnode_line = {},{} usage = {} {}\nnode_p_line = {},{} usage = {} {}\n".format(
            node1.get_id(), node1._pos,
            node2.get_id(), node2._pos,
            gold_line_tuple_a[0].get_id(), gold_line_tuple_a[1].get_id(), start_a, end_a,
            gold_line_tuple_b[0].get_id(), gold_line_tuple_b[1].get_id(), start_b, end_b,
        ))

    # for each internal left point is included, right is not
    end_a -= FLOAT_ERROR
    end_b -= FLOAT_ERROR
    route_list = route_list_a + route_list_b
    for node in route_list:
        if node.get_id() == lca_id:
            continue
        if vis_list[node.get_id()] == 1 or exist(edge_use_dict, node):
            return False

    if add_interval(edge_use_dict, gold_line_tuple_a[0], tuple([start_a, end_a])) and \
       add_interval(edge_use_dict, gold_line_tuple_b[0], tuple([start_b, end_b])) and \
        vis_list[gold_line_tuple_a[0].get_id()] == 0 and \
        vis_list[gold_line_tuple_b[0].get_id()] == 0:
        if start_a < end_a:
            edge_use_dict[gold_line_tuple_a[0]].add(tuple([start_a, end_a]))
        if start_b < end_b:
            edge_use_dict[gold_line_tuple_b[0]].add(tuple([start_b, end_b]))

        for node in route_list:
            if node.get_id() == lca_id:
                continue
            vis_list[node.get_id()] = 1
        return True
    return False


def is_intered(inter1, inter2):
    """
    level: 2
    """
    if inter1[0] == inter1[1] or inter2[0] == inter2[1]:
        return False
    if inter1[0] <= inter2[0] <= inter1[1] or inter1[0] <= inter2[1] <= inter1[1] or \
       inter2[0] <= inter1[0] <= inter2[1] or inter2[0] <= inter1[1] <= inter2[1]:
        return True
    return False


def add_interval(dic, edge, interval):
    """
        level: 2
    """
    if edge not in dic.keys():
        dic[edge] = set()
    if interval[0] > interval[1]:
        return True
    for inter in dic[edge]:
        if is_intered(inter, interval):
            return False
    return True


def get_route_node(current_node, lca_id):
    """
    get all node from current node to the LCA node
    """
    res_list = []
    while not current_node.is_virtual() and not current_node.get_id() == lca_id:
        res_list.append(current_node)
        current_node = current_node.parent
    # if current_node.is_virtual():
    #
    #     raise Exception("[Error: ] something wrong in LCA process")
    res_list.append(current_node)
    return res_list


def exist(dic, edge):
    """
    check if any part of edge is used
    """
    if edge not in dic.keys():
        return False
    if len(dic[edge]) > 0:
        return True
    return False


def swc_get_foot(swc_node, swc_line_tuple):
    e_node = swc_node.get_center()
    e_line = Line(e_node_1=swc_line_tuple[0].get_center(),
                  e_node_2=swc_line_tuple[1].get_center())

    e_foot = e_node.get_closest_point(e_line)
    swc_foot = SwcNode(center=e_foot, radius=1.0, ntype=0)

    return swc_foot
