# bennieHan 2019-11-12 16:01
# all right reserved

from sample.model.swc_node import SwcNode
from sample.model.binary_node import BinaryNode, DEFULT, LEFT, RIGHT

import queue
import math
import time
import queue
import copy

FLOAT_INF = 999999999.9

# read a swcfile and convert it into a swc node tree
# input: file path
# output: a list of swc tree roots
def swcfile_to_swcnodelist(file_name):
    swc_tree_list = []
    id_swcnode_map = {}
    node_ids = set()

    with open(file_name) as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue

            id, type, x, y, z, r, pid = map(float, line.split())
            current_node = SwcNode(id,1,pid,[],x,y,z,r)

            if id in node_ids:
                error = "[Error:read_swc:15] Node id " + str(id) + " has exist!"
                raise Exception(error)
            node_ids.add(id)
            id_swcnode_map[id] = current_node

            if pid == -1:
                swc_tree_list.append(current_node)
            elif pid not in node_ids:
                error = "[Error:read_swc:23] Node id " + str(id) + " 's parent doesn't exist!"
                raise Exception(error)
            else:
                parent_node = id_swcnode_map[pid]
                parent_node.son.append(current_node)
    return swc_tree_list

def get_distance(node1, node2):
    comp1 = None
    comp2 = None
    if type(node1) == type(BinaryNode()):
        comp1 = node1.data
    else:
        comp1 = node1

    if type(node2) == type(BinaryNode()):
        comp2 = node2.data
    else:
        comp2 = node2

    dx = comp1.x - comp2.x
    dy = comp1.y - comp2.y
    dz = comp1.z - comp2.z
    return math.sqrt(dx*dx+dy*dy+dz*dz)

# recurrently convert a swcnode tree into a binary tree
# input: root of a swcnode tree
# return: root of a binary tree
def swctree_to_binarytree(node):
    binary_root = BinaryNode(data=node)

    # the nodes in this list is the root of a binary tree
    binnary_son_list = []
    for son_node in node.son:
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
                if get_distance(bin_node1, bin_node2) < distance:
                    best1 = bin_node1
                    best2 = bin_node2
                    distance = get_distance(bin_node1, bin_node2)

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
        bin_node.max_dep = max(bin_node.max_dep, bin_node.left_son.max_dep+1)
        bin_node.treesize += bin_node.left_son.treesize

    if bin_node.right_son is not None:
        isleaf = False
        re_arrange(bin_node=bin_node.right_son, hight=hight+1, parent=bin_node,side=RIGHT)
        bin_node.max_dep = max(bin_node.max_dep, bin_node.rigt_son.max_dep + 1)
        bin_node.treesize += bin_node.right_son.treesize

# calculate the distance to root
def calculate_trajectories(bin_root, thresholds, z_in_path_dist = True, current_trajectories = 0.0):
    pass


# testfunction:
# input: a swc tree root
# return: none
# print the whole tree
def test_print_tree(root_node):
    num = 0
    q = queue.Queue()
    q.put(root_node)
    while not q.empty():
        num += 1
        cur = q.get()
        print(cur.id)
        for item in cur.son:
            print(item.id)
            q.put(item)
        print("-----------")
    print("tree node num = {}".format(num))

def test_print_bin_tree(root_node):
    num = 0
    q = queue.Queue()
    q.put(root_node)
    while not q.empty():
        num += 1
        cur = q.get()
        print(cur.data.id)
        if cur.left_son != None:
            print(cur.left_son.data.id)
            q.put(cur.left_son)
        if cur.right_son != None:
            print(cur.right_son.data.id)
            q.put(cur.right_son)
        print("-----------")
    print("tree node num = {}".format(num))

#　测试说明：
# set的查找比list快很多,set和list黄转换挺快的，set到list更快一点
def test1():
    a = set()
    start = time.time()
    for i in range(10000000):
        a.add(i)
    print(time.time() - start)
    a = list(a)
    print(time.time() - start)
    a = set(a)
    print(time.time() - start)
    num = 0
    for i in range(5000000,15000000):
        if i in a:
            num += 1;
    print(num)
    print(time.time() - start)

# 测试一下读入整棵树的时间
def test2():
    start = time.time()
    tree = swcfile_to_swcnodelist(file_name="..\..\\test\data_example\ExampleTest.swc")
    # test_print_tree(tree[0])
    # bin_tree = swctree_to_binarytree(tree[0])
    print(time.time() - start)

if __name__ == "__main__":
    test2()
