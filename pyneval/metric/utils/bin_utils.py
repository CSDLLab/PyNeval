from anytree import NodeMixin
from pyneval.model.euclidean_point import EuclideanPoint
from pyneval.model.binary_node import BinaryNode

import copy
import math
import queue

_3D = "3d"
_2D = "2d"
TRAJECTORY_NONE = -1.0
FLOAT_INF = 999999999.9
RIGHT = 'right'
LEFT = 'left'
DEFULT = 'DEFULT'


# recurrently convert a swcnode tree into a binary tree
# input: root of a swcnode tree
# return: root of a binary tree
def swctree_to_binarytree(node):
    binary_root = BinaryNode(data=node)

    # the nodes in this list is the root of a binary tree
    binnary_son_list = []
    son = list(node.children)

    for son_node in son:
        # print(type(son_node))
        binnary_node = swctree_to_binarytree(son_node)
        binnary_son_list.append(binnary_node)

    while len(binnary_son_list) > 2:
        best1 = binnary_son_list[0]
        best2 = binnary_son_list[1]
        distance = FLOAT_INF
        for i in range(len(binnary_son_list)- 1):
            bin_node1 = binnary_son_list[i]
            for j in range(i+1, len(binnary_son_list)):
                bin_node2 = binnary_son_list[j]
                if bin_node1.data.distance(bin_node2.data) < distance:
                    best1 = bin_node1
                    best2 = bin_node2
                    distance = bin_node1.data.distance(bin_node2.data)

        # new_swcnode = copy.copy(node)
        new_binnode = BinaryNode(data=node, left_son=best1, right_son=best2)
        binnary_son_list.remove(best1)
        binnary_son_list.remove(best2)
        binnary_son_list.append(new_binnode)

    if len(binnary_son_list) >= 1:
        binary_root.left_son = binnary_son_list[0]
    if len(binnary_son_list) == 2:
        binary_root.right_son = binnary_son_list[1]

    return binary_root


def re_arrange(bin_node, hight=1, parent=None, side=DEFULT):
    bin_node.hight = hight
    bin_node.parent = parent
    bin_node.side = side
    bin_node.max_dep = 1
    bin_node.treesize = 1
    if bin_node.left_son is not None:
        re_arrange(bin_node=bin_node.left_son, hight=hight+1, parent=bin_node, side=LEFT)
        bin_node.max_dep = max(bin_node.max_dep, bin_node.left_son.max_dep + 1)
        bin_node.treesize += bin_node.left_son.treesize

    if bin_node.right_son is not None:
        re_arrange(bin_node=bin_node.right_son, hight=hight+1, parent=bin_node,side=RIGHT)
        bin_node.max_dep = max(bin_node.max_dep, bin_node.right_son.max_dep + 1)
        bin_node.treesize += bin_node.right_son.treesize


def calculate_trajectories_xy(origin, first, second, threshold):
    point = EuclideanPoint(center=[0,0,0])

    to_first = origin.distance(first, _2D)
    to_second = origin.distance(second, _2D)

    proportionAlongLine = (threshold - to_first)/(to_second - to_first)

    point.set_x(first.get_x() + proportionAlongLine*(second.get_x() - first.get_x()))
    point.set_y(first.get_y() + proportionAlongLine*(second.get_y() - first.get_y()))
    return point


def calculate_trajectories_z(origin, first, second, threshold):
    to_first = math.fabs(origin.get_z() - first.get_z())
    to_second = math.fabs(origin.get_z() - second.get_z())

    proportionAlongLine = (threshold - to_first)/(to_second - to_first)

    return first.get_z() + proportionAlongLine*(second.get_z() - first.get_z())


def find_parent_trajectory(node, thereholds, DEBUG=False):
    done_x = False
    done_z = False
    xy_dis = 0.0
    z_dis = 0.0

    c = node
    data = node.data
    c_data = c.data

    point = EuclideanPoint(center=[0,0,0])
    while not done_x or not done_z:
        c = c.parent
        prev_data = c_data
        c_data = c.data
        if not done_x:
            xy_dis = data.distance(c_data, _2D)
            if xy_dis > thereholds.get_x():
                tmp_point = EuclideanPoint(center=[0, 0, 0])
                tmp_point.add_coord(calculate_trajectories_xy(data, prev_data, c_data, thereholds.get_x()))
                point.set_x(tmp_point.get_x())
                point.set_y(tmp_point.get_y())
                done_x = True
            elif c.is_root:
                point.set_x(c_data.get_x())
                point.set_y(c_data.get_y())
                done_x = True

        if not done_z:
            z_dis = math.fabs(data.get_z() - c_data.get_z())
            if z_dis > thereholds.get_z():
                point.set_z(calculate_trajectories_z(data, prev_data, c_data, thereholds.get_z()))
                done_z = True
            elif c.is_root:
                point.set_z(c_data.get_z())
                done_z = True
    if DEBUG:
        print(node.data._id)
        print("trx = {}, try = {}, trz = {}".format(point.get_x(), point.get_y(), point.get_z()))
        print("----------------------------------------------------------------")
    return point


def find_child_trajectory(data, child, thresholds, DEBUG=False):
    xy_dis = 0.0
    z_dis = 0.0
    done_x = False
    done_z = False
    prev_data = data

    point = EuclideanPoint(center=[0, 0, 0])
    while not done_x or not done_z:
        c_data = child.data

        if not done_x:
            xy_dis = data.distance(c_data, _2D)

            if xy_dis > thresholds.get_x():
                tmp_point = EuclideanPoint(center=[0, 0, 0])
                tmp_point.add_coord(calculate_trajectories_xy(data, prev_data, c_data, thresholds.get_x()))
                point.set_x(tmp_point.get_x())
                point.set_y(tmp_point.get_y())
                done_x = True
            elif child.is_leaf():
                point.set_x(c_data.get_x())
                point.set_y(c_data.get_y())
                done_x = True
            elif child.right_son != None:
                point.set_x(TRAJECTORY_NONE)
                point.set_y(TRAJECTORY_NONE)
                done_x = True

        if not done_z:
            z_dis = math.fabs(data.get_z() - c_data.get_z())
            if z_dis > thresholds.get_z():
                point.set_z(calculate_trajectories_z(data, prev_data, c_data, thresholds.get_z()))
                done_z = True
            elif child.is_leaf():
                point.set_z(c_data.get_z())
                done_z = True
            elif child.right_son != None:
                point.set_z(TRAJECTORY_NONE)
                done_z = True

        prev_data = c_data
        if not child.is_leaf():
            child = child.left_son

    if DEBUG:
        print(data.id)
        print("trx = {}, try = {}, trz = {}".format(point.get_x(), point.get_y(), point.get_z()))
        print("----------------------------------------------------------------")
    return point


def add_child_bifurcations(stack, node):
    lson = node.left_son
    rson = node.right_son

    while lson.left_son is not None and lson.right_son is None:
        lson = lson.left_son
    stack.put(lson)

    while rson.left_son is not None and rson.right_son is None:
        rson = rson.left_son
    stack.put(rson)


# calculate the distance to root
def calculate_trajectories(swc_root, bin_root, thresholds, z_in_path_dist =True, current_trajectories=0.0, DEBUG=False):
    stack = queue.LifoQueue()

    node = bin_root
    while node.left_son != None and node.right_son == None:
        node = node.left_son
    stack.put(node)

    while not stack.empty():
        node = stack.get()
        if DEBUG:
            print("[debug:  ] calculate trajectories for node {}".format(node.data.get_id()))
        data = node.data

        if data.parent_trajectory is None:
            data.parent_trajectory = EuclideanPoint(center=[0, 0, 0])
        if not node.is_root():
            data.parent_trajectory.add_coord(find_parent_trajectory(node, thresholds))
        else:
            tmp_pa = BinaryNode(data=swc_root)
            node.parent = tmp_pa
            data.parent_trajectory.add_coord(find_parent_trajectory(node, thresholds))
            node.parent = None

        if not node.is_leaf():
            if data.left_trajectory is None:
                data.left_trajectory = EuclideanPoint(center=[0, 0, 0])
            if data.right_trajectory is None:
                data.right_trajectory = EuclideanPoint(center=[0, 0, 0])
            data.left_trajectory.add_coord(find_child_trajectory(data, node.left_son, thresholds))
            data.right_trajectory.add_coord(find_child_trajectory(data, node.right_son, thresholds))
            add_child_bifurcations(stack, node)

        if DEBUG:
            print("trajectory:")
            if data.parent_trajectory is not None:
                print("pa_tra = {}".format(data.parent_trajectory._pos))
            if data.left_trajectory is not None:
                print("left_tra = {}".format(data.left_trajectory._pos))
            if data.right_trajectory is not None:
                print("right_tra = {}".format(data.right_trajectory._pos))


def calculate_path_data(bin_node, z_in_path_dist, DEBUG=False):
    data = bin_node.data
    pa_data = bin_node.parent.data
    if pa_data.get_id() == -1:
        return

    if data.path_length == 0.0:
        if z_in_path_dist:
            data.path_length = data.distance(pa_data)
            data.xy_path_length = data.distance(pa_data, mode=_2D)
        else:
            data.path_length = data.distance(pa_data, mode=_2D)
            data.xy_path_length = data.distance(pa_data, mode=_2D)
        data.z_path_length = math.fabs(pa_data.get_z() - data.get_z())
        data.surface_area = data.path_length*math.pi*data.radius()*2
        data.volume = data.path_length*math.pi*data.radius()*data.radius()
    if DEBUG:
        print("node_id = {}, path = {}, xy_path = {}, z_path = {}".format(data._id,
                                                                          data.path_length,
                                                                          data.xy_path_length,
                                                                          data.z_path_length))


def remove_continuations(swc_root, bin_root, calc_path_dist, z_in_path_dist):
    stack = queue.LifoQueue()

    # swc_node: data
    child_data = None

    # bin_node: node
    res_root = bin_root
    child = None

    if calc_path_dist:
        data = bin_root.data

        if z_in_path_dist:
            data.path_length = swc_root.distance(data)
            data.xy_path_length = swc_root.distance(data, mode="2d")
        else:
            data.path_length = swc_root.distance(data, mode="2d")
            data.xy_path_length = swc_root.distance(data, mode="2d")
        data.z_path_length = math.fabs(swc_root.get_z() - bin_root.data.get_z())

    stack.put(bin_root)
    while not stack.empty():
        node = stack.get()
        data = node.data

        if not node.is_leaf():
            stack.put(node.left_son)
            if calc_path_dist:
                calculate_path_data(node.left_son, z_in_path_dist)
            if node.right_son is None:
                # prepare to remove the node
                child = node.left_son
                child_data = child.data
                if calc_path_dist:
                    child_data.add_data(data)
                if node == res_root:
                    res_root = child
                    child.parent = None
                else:
                    if node.get_side() == LEFT:
                        node.parent.left_son = child
                    elif node.get_side() == RIGHT:
                        node.parent.right_son = child
                    child.parent = node.parent
            else:
                stack.put(node.right_son)
                if calc_path_dist:
                    calculate_path_data(node.right_son, z_in_path_dist)
    return res_root


def convert_to_binarytree(tot_root, swc_root):
    # swc_tree._print()
    bintree_root = swctree_to_binarytree(swc_root)
    # debug
    # bintree_root.print_tree()

    re_arrange(bintree_root)
    calculate_trajectories(swc_root=tot_root,
                           bin_root=bintree_root,
                           thresholds=EuclideanPoint([1.2,0,0]),
                           z_in_path_dist=True)

    bintree_root = remove_continuations(swc_root=tot_root,
                                        bin_root=bintree_root,
                                        calc_path_dist=True,
                                        z_in_path_dist=False)
    return bintree_root


def convert_to_binarytrees(root):
    tot_root = BinaryNode(data=root)
    bin_root_list = []
    for node in root.children:
        bin_node = convert_to_binarytree(root, node)
        bin_root_list.append(bin_node)
    return tot_root, bin_root_list
