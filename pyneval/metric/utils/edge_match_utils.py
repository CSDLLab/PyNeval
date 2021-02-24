import numpy as np
import math
from rtree import index

from pyneval.model import euclidean_point as euc_p
from pyneval.metric.utils import config_utils
from pyneval.model import swc_node


def get_match_edges(gold_swc_tree=None, test_swc_tree=None,
                    rad_threshold=-1.0, len_threshold=0.2,
                    debug=False):
    """
    get matched edge set
    Args:
        gold_swc_tree(SwcTree):
        test_swc_tree(SwcTree):
        rad_threshold(float): threshold of key point radius
        len_threshold(float): threshold of length of the matching edges
        debug(bool): list debug info ot not
    Returns:
        match_edge(set): include all edge that are matched in gold swc tree
            edge(tuple): every edge is a tuple contains two side nodes of a edge
        test_match_length(float): it's the total length of matched area on test swc tree
    Raises:
        [Error: ] Max id in test swc tree too large
            the size of vis list is depend on the maximum id of the tree.
            this number couldn't be too large

    """

    match_edge = set()
    edge_use_dict = {}
    id_rootdis_dict = {}
    test_match_length = 0.0

    test_rtree = get_edge_rtree(test_swc_tree)
    id_edge_dict = get_idedge_dict(test_swc_tree)
    gold_node_list = gold_swc_tree.get_node_list()
    test_node_list = test_swc_tree.get_node_list()

    # node num need to be larger than the max id
    test_maxum = 0
    for node in test_node_list:
        id_rootdis_dict[node.get_id()] = node.root_length
        test_maxum = max(test_maxum, node.get_id())

    try:
        vis_list = np.zeros(test_maxum+5, dtype='int8')
        test_swc_tree.get_lca_preprocess(node_num=test_maxum+5)
    except:
        raise Exception("[Error: ] Max id in test swc tree too large")

    for node in gold_node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        rad_threshold1, rad_threshold2 = cal_rad_threshold(rad_threshold, node.radius(), node.parent.radius())

        line_tuple_a_set = get_nearby_edges(rtree=test_rtree, point=node, id_edge_dict=id_edge_dict,
                                            threshold=rad_threshold1, not_self=False, debug=debug)
        line_tuple_b_set = get_nearby_edges(rtree=test_rtree, point=node.parent, id_edge_dict=id_edge_dict,
                                            threshold=rad_threshold2, not_self=False, debug=debug)

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
                               euc_p.Line(e_node_1=node.get_center(),
                                          e_node_2=node.parent.get_center()),
                               id_rootdis_dict)
                gold_length = node.parent_distance()

                if test_length == config_utils.DINF:
                    continue

                len_threshold1 = cal_len_threshold(len_threshold, gold_length)
                if not (dis_a <= rad_threshold1 and dis_b <= rad_threshold2):
                    if debug:
                        print(node.get_id(), dis_a, rad_threshold1, dis_b, rad_threshold2, "error1")
                    continue
                if not (math.fabs(test_length - gold_length) < len_threshold1):
                    if debug:
                        print(node.get_id(), "error2")
                    continue
                if not is_route_clean(gold_swc_tree=test_swc_tree,
                                      gold_line_tuple_a=line_tuple_a, gold_line_tuple_b=line_tuple_b,
                                      node1=node, node2=node.parent,
                                      edge_use_dict=edge_use_dict, vis_list= vis_list, debug=debug):
                    if debug:
                        print(node.get_id(), "error3")
                    continue
                match_edge.add(tuple([node, node.parent]))
                test_match_length += test_length
                done = True
                break

        if not done:
            node._type = 9
            if debug:
                print("{} not done".format(node.get_id()))

    return match_edge, test_match_length


def get_edge_rtree(swc_tree=None):
    """
    build a rtree based on the swc tree
    Args：
        swc_tree(Swc Tree): Swc_Tree, to build rtree
    Return:
        rtree(rtree index)
    """
    swc_tree_list = swc_tree.get_node_list()
    p = index.Property()
    p.dimension = 3
    rtree = index.Index(properties=p)
    for node in swc_tree_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        rtree.insert(node.get_id(), get_bounds(node, node.parent, extra=node.radius()))
    return rtree


def get_bounds(point_a, point_b, extra=0):
    """
    get bounding box of a segment
    Args:
        point_a: two points to identify the square
        point_b:
        extra: float, a threshold
    Return:
        res(tuple):
    """
    point_a = np.array(point_a.get_center()._pos)
    point_b = np.array(point_b.get_center()._pos)
    res = (np.where(point_a > point_b, point_b, point_a) - extra).tolist() + (np.where(point_a > point_b, point_a, point_b) + extra).tolist()

    return tuple(res)


def get_idedge_dict(swc_tree=None):
    '''
    get a dict, mapping from id to edge.
    id_edge_dict[swc_node1.id] = tuple(swc_node1, swc_node2)
    Args:
        swc_tree:
    Return:
        id_edge_dict(Dict)
        key: son node's id
        value: tuple(node, node.parent)
    '''
    id_edge_dict = {}
    swc_tree_list = swc_tree.get_node_list()
    for node in swc_tree_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        id_edge_dict[node.get_id()] = tuple([node, node.parent])
    return id_edge_dict


def cal_rad_threshold(rad_threshold, dis1, dis2):
    """
    TODO: Negative value of threshold is not recommand. Waiting to be modified.
    """
    if rad_threshold < 0:
        return -rad_threshold*dis1, -rad_threshold*dis2
    else:
        return rad_threshold, rad_threshold


def cal_len_threshold(len_threshold, length):
    return length * len_threshold


def get_nearby_edges(rtree, point, id_edge_dict, threshold, not_self=False, debug=False):
    '''
    find the close enough edges of a node base on rtree
    sorted by distance
    Args:
        rtree(): an rtree describe the target edge set
        point: the point to get nearby edges
        id_edge_dict:map between id and line tuple(edge)
        threshold: the ceiling of the distance between point and edge
        not_self: exclude self, used in overlap detect
        debug:
    Returns:
         a list of tuple(edge, dis). Sorted according to distance to the point
    level: 1
    '''
    point_box = (point.get_x() - threshold, point.get_y() - threshold, point.get_z() - threshold,
                 point.get_x() + threshold, point.get_y() + threshold, point.get_z() + threshold)
    hits = list(rtree.intersection(point_box))
    nearby_edges = []

    for h in hits:
        line_tuple = id_edge_dict[h]
        if debug:
            print("\npoint = id{} poi{}, line_a = id{} poi{}, line_b = id{} poi{}".format(
                point.get_id(), point.get_center()._pos,
                line_tuple[0].get_id(), line_tuple[0].get_center()._pos,
                line_tuple[1].get_id(), line_tuple[1].get_center()._pos)
            )
        e_point = point.get_center()

        # if two sides of line_tuple is in the same position, ignore this line
        if line_tuple[0].get_center().distance(line_tuple[1].get_center()) == 0:
            continue

        new_d = e_point.distance(euc_p.Line(e_node_1=line_tuple[0].get_center(), e_node_2=line_tuple[1].get_center()))
        if not_self and new_d == 0:
            continue
        nearby_edges.append(tuple([line_tuple, new_d]))
    nearby_edges.sort(key=lambda x: x[1])
    return nearby_edges


def get_lca_length(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, test_line, id_rootdis_dict):
    """
    calculate the length of the path on gold_swc_tree corresponding to test line
    This function get the foot of two side nodes of test_line first.
    than calculate the distance between two foots.
    Args:
        gold_swc_tree(SwcTree): swc tree that are calculated.
        gold_line_tuple_a(tuple): a list of two nodes describe a edge
        gold_line_tuple_b(tuple): a list of two nodes describe a edge
        test_line(Line): Line object defined in pyneval/model/euclidean_point
        id_rootdis_dict(Dict): a dict [int to float], get nodes' distance to root by its id
    Return:
        lca_length(float): distance of two foot of side nodes of test line
    """
    point_a, point_b = test_line.get_points()

    gold_line_a = euc_p.Line(e_node_1=gold_line_tuple_a[0].get_center(),
                             e_node_2=gold_line_tuple_a[1].get_center())
    gold_line_b = euc_p.Line(e_node_1=gold_line_tuple_b[0].get_center(),
                             e_node_2=gold_line_tuple_b[1].get_center())

    foot_a = point_a.get_closest_point(gold_line_a)
    foot_b = point_b.get_closest_point(gold_line_b)

    # if two foots lay on the same edge, pass
    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
        gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
        return foot_a.distance(foot_b)

    lca_id = gold_swc_tree.get_lca(gold_line_tuple_a[0].get_id(), gold_line_tuple_b[0].get_id())
    if lca_id is None or lca_id < 1:
        return config_utils.DINF
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

    return lca_length


def is_route_clean(gold_swc_tree, gold_line_tuple_a, gold_line_tuple_b, node1, node2, edge_use_dict, vis_list, debug):
    """
    Check if all edge between two euc nodes are totally unused.
    for any edge, we constructed a data structure call interval, recording witch parts of the edge are used.
    so this function will call add_interval, is_intered to change the useage of the edge.
    Args:
        gold_swc_tree(SwcTree) swc tree that are calculated.
        gold_line_tuple_a(tuple): a list of two nodes describe a edge
        gold_line_tuple_b(tuple): a list of two nodes describe a edge
        node1(Swc_Node): one node side
        node2(Swc_Node): the other node side
        edge_use_dict(Dict):
            example: [swc_node, list[interval_1, interval_2]]
            interval is a tuple of two integers,
            edge_use_dict shows which part of edge between swc_node and swc_node.parent has been used
        vis_list: list, check if whole edge has been used
    Return:
        True/False
    """
    point_a = node1.get_center()
    point_b = node2.get_center()
    gold_line_a = euc_p.Line(e_node_1=gold_line_tuple_a[0].get_center(),
                             e_node_2=gold_line_tuple_a[1].get_center())
    gold_line_b = euc_p.Line(e_node_1=gold_line_tuple_b[0].get_center(),
                             e_node_2=gold_line_tuple_b[1].get_center())

    foot_a = point_a.get_closest_point(gold_line_a)
    foot_b = point_b.get_closest_point(gold_line_b)

    # if two foots lay on the same edge, pass
    if gold_line_tuple_a[0].get_id() == gold_line_tuple_b[0].get_id() and \
        gold_line_tuple_a[1].get_id() == gold_line_tuple_b[1].get_id():
            total_length = gold_line_tuple_a[0].distance(gold_line_tuple_a[1])
            start = foot_a.distance(gold_line_tuple_a[0].get_center()) / total_length
            end = foot_b.distance(gold_line_tuple_a[0].get_center()) / total_length
            if debug:
                print("node = {} {}\nnode.parent = {} {}\nnode_line = {},{} usage = {} {}\n".format(
                        node1.get_id(), node1.get_center()._pos,
                        node2.get_id(), node2.get_center()._pos,
                        gold_line_tuple_a[0].get_id(), gold_line_tuple_a[1].get_id(), start, end,
                    ))
            if start > end:
                start, end = end, start
            end -= config_utils.FLOAT_ERROR
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

    if debug:
        print("\nnode = {} {}\nnode.parent = {} {}\nnode_line = {},{} usage = {} {}\nnode_p_line = {},{} usage = {} {}\n".format(
            node1.get_id(), node1._pos,
            node2.get_id(), node2._pos,
            gold_line_tuple_a[0].get_id(), gold_line_tuple_a[1].get_id(), start_a, end_a,
            gold_line_tuple_b[0].get_id(), gold_line_tuple_b[1].get_id(), start_b, end_b,
        ))

    # for each internal left point is included, right is not
    end_a -= config_utils.FLOAT_ERROR
    end_b -= config_utils.FLOAT_ERROR
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
    check if two inters has intersection
    inter are just tuplas for two side nodes: both left and right are closed interval [... , ...]
    """
    if inter1[0] == inter1[1] or inter2[0] == inter2[1]:
        return False
    if inter1[0] <= inter2[0] <= inter1[1] or inter1[0] <= inter2[1] <= inter1[1] or \
       inter2[0] <= inter1[0] <= inter2[1] or inter2[0] <= inter1[1] <= inter2[1]:
        return True
    return False


def add_interval(dic, edge, interval):
    """
        add a interval to the edge.
        demonstrate this part of the edge has been used.

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
