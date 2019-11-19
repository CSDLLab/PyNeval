# bennieHan 2019-11-12 16:01
# all right reserved

from sample.model.swc_node import SwcNode
from sample.model.binary_node import BinaryNode, DEFULT, LEFT, RIGHT
# from sample.util.read_swc import swcfile_to_swcnodelist,swctree_to_binarytree
import queue
import math
import time
import queue
import copy

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
        # num += 1
        cur = q.get()
        # print(cur.data.id)
        if ((cur.left_son != None and cur.right_son != None) or \
               (cur.left_son == None and cur.right_son == None)):
            print("node_id = {}, Left = {}, Right = {}".format(cur.data.id,cur.left_son, cur.right_son))
            print("出大问题！")
            num += 1
        if cur.left_son != None:
            # print(cur.left_son.data.id)
            q.put(cur.left_son)
        if cur.right_son != None:
            # print(cur.right_son.data.id)
            q.put(cur.right_son)
        # print("-----------")
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
    tree = swcfile_to_swcnodelist(file_name="..\..\\test\data_example\ExampleGoldStandard.swc")
    bin_tree = swctree_to_binarytree(tree[0])
    test_print_bin_tree(bin_tree)
    print(time.time() - start)

if __name__ == "__main__":
    test2()