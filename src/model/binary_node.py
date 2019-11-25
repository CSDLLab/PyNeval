from anytree import NodeMixin
from src.model.swc_node import SwcTree
from src.model.euclidean_point import EuclideanPoint
from test.convert_to_binary_test_function import test_print_bin_tree

import os
import math
import queue
import copy

_3D = "3d"
_2D = "2d"
TRAJECTORY_NONE = -1.0
FLOAT_INF = 999999999.9
DEBUG = False
RIGHT = 'right'
LEFT = 'left'
DEFULT = 'DEFULT'


class BinaryNode(NodeMixin):
    """
        this is a class that temporarily store binarytree transformed from swcTree
        Attributes:
        id: id of the node,
        type: leaf = 1,continuation = 2, bifurcation = 3,
        parent: pa node id,
        son=[]: son list,
        x: x coordinate,
        y: y coordinate,
        z: z coordinate,
        radius: radius of the node
    """

    def __init__(self,
                 data=object,
                 parent=None,
                 left_son=None,
                 right_son=None,

                 max_dep=0,
                 hight=0,
                 treesize=1,
                 leaves=1):
        self.data=data
        self.parent=parent
        self.left_son=left_son
        self.right_son=right_son
        self.max_dep=max_dep
        self.hight=hight
        self.treesize=treesize

    def has_children(self):
        if self.left_son is not None or self.right_son is not None:
            return True
        return False

    def get_side(self):
        if self.is_root():
            return DEFULT
        if self.parent.left_son == self:
            return LEFT
        if self.parent.right_son == self:
            return RIGHT
        raise Exception("[Error:  ] node {} is not its parent's son".format(self.data.id))

    def is_root(self):
        if self.parent == None:
            return True
        return False

    def is_leaf(self):
        if self.left_son == None and self.right_son == None:
            return True
        return False

# recurrently convert a swcnode tree into a binary tree
# input: root of a swcnode tree
# return: root of a binary tree
def swctree_to_binarytree(node):
    binary_root = BinaryNode(data=node)

    # the nodes in this list is the root of a binary tree
    binnary_son_list = []
    son = list(node.children)

    for son_node in son:
        print(type(son_node))
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

        new_swcnode = copy.deepcopy(node)
        new_binnode = BinaryNode(data=new_swcnode,left_son=best1,right_son=best2)
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
    point = EuclideanPoint()

    to_first = origin.distance(first)
    to_second = origin.distance(second)

    proportionAlongLine = (threshold - to_first)/(to_second - to_first)

    point._pos[0] = (first._pos[0] + proportionAlongLine*(second._pos[0] - first._pos[0]))
    point._pos[1] = (first._pos[1] + proportionAlongLine*(second._pos[1] - first._pos[1]))
    return point

def calculate_trajectories_z(origin, first, second, threshold):
    to_first = math.fabs(origin._pos[2] - first._pos[2])
    to_second = math.fabs(origin._pos[2] - second._pos[2])

    proportionAlongLine = (threshold - to_first)/(to_second - to_first)

    return first._pos[2] + proportionAlongLine*(second._pos[2] - first._pos[2])

def find_parent_trajectory(node, thereholds):
    done_x = False
    done_z = False
    xy_dis = 0.0
    z_dis = 0.0

    c = node
    data = node.data
    c_data = c.data

    point = EuclideanPoint()
    while not done_x or not done_z:
        c = c.parent
        prevData = c_data
        c_data = c.data
        if not done_x:
            xy_dis = data.distance(c_data)
            if xy_dis > thereholds._pos[0]:
                tmp_point = calculate_trajectories_xy(data, prevData, c_data, thereholds._pos[0])
                point._pos[0] = tmp_point._pos[0]
                point._pos[1] = tmp_point._pos[1]
                done_x = True
            elif c.is_root:
                point._pos[0] = c_data._pos[0]
                point._pos[1] = c_data._pos[1]
                done_x = True

        if not done_z:
            z_dis = math.fabs(data._pos[2] - c_data._pos[2])
            if z_dis > thereholds._pos[2]:
                point._pos[2] = calculate_trajectories_z(data, prevData, c_data, thereholds._pos[2])
                done_z = True
            elif c.is_root:
                point._pos[2] = c_data._pos[2]
                done_z = True
    if DEBUG:
        print(node.data._id)
        print("trx = {}, try = {}, trz = {}".format(point._pos[0], point._pos[1], point._pos[2]))
        print("----------------------------------------------------------------")
    return point

def find_child_trajectory(data, child, thresholds):
    xy_dis = 0.0
    z_dis = 0.0
    done_x = False
    done_z = False
    prev_data = data

    point = EuclideanPoint()
    while not done_x or not done_z:
        c_data = child.data

        if not done_x:
            xy_dis = data.distance(c_data)

            if xy_dis > thresholds._pos[0]:
                tmp_point = calculate_trajectories_xy(data, prev_data, c_data, thresholds._pos[0])
                point._pos[0] = tmp_point._pos[0]
                point._pos[1] = tmp_point._pos[1]
                done_x = True
            elif child.is_leaf():
                point._pos[0] = c_data._pos[0]
                point._pos[1] = c_data._pos[1]
                done_x = True
            elif child.right_son != None:
                point._pos[0] = TRAJECTORY_NONE
                point._pos[1] = TRAJECTORY_NONE
                done_x = True

        if not done_z:
            z_dis = math.fabs(data._pos[2] - c_data._pos[2])
            if z_dis > thresholds._pos[2]:
                point._pos[2] = calculate_trajectories_z(data, prev_data, c_data, thresholds._pos[2])
                done_z = True
            elif child.is_leaf():
                point._pos[2] = c_data._pos[2]
                done_z = True
            elif child.right_son != None:
                point._pos[2] = TRAJECTORY_NONE
                done_z = True

        prev_data = c_data
        if not child.is_leaf():
            child = child.left_son

    if DEBUG:
        print(data.id)
        print("trx = {}, try = {}, trz = {}".format(point._pos[0], point._pos[1], point._pos[2]))
        print("----------------------------------------------------------------")
    return point

def add_child_bifurcations(stack, node):
    lson = node.left_son
    rson = node.right_son

    while lson.left_son != None and lson.right_son == None:
        lson = lson.left_son
    stack.put(lson)

    while rson.left_son != None and rson.right_son == None:
        rson = rson.left_son
    stack.put(rson)

# calculate the distance to root
def calculate_trajectories(bin_root, thresholds, z_in_path_dist = True, current_trajectories = 0.0):
    stack = queue.LifoQueue()

    node = bin_root
    while node.left_son != None and node.right_son == None:
        node = node.left_son
    stack.put(node)

    while not stack.empty():
        node = stack.get()
        if DEBUG:
            print("[debug:  ] calculate trajectories for node {}".format(node.data.id))
        data = node.data

        if not node.is_root():
            data.parent_trajectory = find_parent_trajectory(node, thresholds)

        if not node.is_leaf():
            data.left_trajectory = find_child_trajectory(data, node.left_son, thresholds)
            data.right_trajectory = find_child_trajectory(data, node.right_son, thresholds)
            add_child_bifurcations(stack, node)

def calculate_path_data(bin_node, z_in_path_dist):
    data = bin_node.data
    pa_data = bin_node.parent.data

    if data.path_length == 0.0:
        if z_in_path_dist:
            data.path_length = data.distance(pa_data)
            data.xy_path_length = data.distance(pa_data,mode=_2D)
        else:
            data.path_length = data.distance(pa_data,mode=_2D)
            data.xy_path_length = data.distance(pa_data,mode=_2D)
        data.z_path_length = math.fabs(pa_data._pos[2] - data._pos[2])
        data.surface_area = data.path_length*math.pi*data.radius()*2
        data.volume = data.path_length*math.pi*data.radius()*data.radius()
    if DEBUG:
        print("node_id = {}, path = {}, xy_path = {}, z_path = {}".format(data._id,
                                                                          data.path_length,
                                                                          data.xy_path_length,
                                                                          data.z_path_length))

def remove_continuations(swc_root, bin_root, calc_path_dist,z_in_path_dist):
    stack = queue.LifoQueue()

    # swc_node: data
    data = None
    child_data = None

    # bin_node: node
    res_root = bin_root
    child = None

    stack.put(bin_root)
    while not stack.empty():
        node = stack.get()
        data = node.data
        if not node.is_leaf():
            stack.put(node.left_son)
            if calc_path_dist:
                calculate_path_data(node.left_son, z_in_path_dist)
            if node.right_son == None:
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

def convert_to_binarytree(swc_file_path):
    swc_tree = SwcTree()
    swc_tree.load(swc_file_path)

    if swc_tree.node_count() == 0:
        raise Exception("[Error:  read file Error]" + "read " + swc_file_path + " fail. Maybe file has been broken")
        return None
    elif swc_tree.node_count() > 1:
        print("[Warning:  ] More than one swc tree detected. Only the first one will be used")

    bintree_root = swctree_to_binarytree(swc_tree.root())
    re_arrange(bintree_root)
    calculate_trajectories(bin_root=bintree_root,
                           thresholds=EuclideanPoint([1.2,0,0]),
                           z_in_path_dist=True)

    bintree_root = remove_continuations(swc_root=swc_tree.root(),
                                        bin_root=bintree_root,
                                        calc_path_dist=True,
                                        z_in_path_dist=True)
    test_print_bin_tree(bintree_root)
    return bintree_root

# if path is a fold
def convert_path_to_binarytree(swc_file_paths):
    bintree_root_list = []
    if os.path.isfile(swc_file_paths):
        if not (swc_file_paths[-4:] == ".swc" or swc_file_paths[-4:] == ".SWC"):
            print(swc_file_paths + "is not a tif file")
            return None
        bintree_root_list.append(convert_to_binarytree(swc_file_paths))
    elif os.path.isdir(swc_file_paths):
        for file in os.listdir(swc_file_paths):
            bintree_root_list += convert_path_to_binarytree(swc_file_paths=os.path.join(swc_file_paths, file))
    return bintree_root_list