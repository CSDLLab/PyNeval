# bennieHan 2019-11-12 16:01
# all right reserved

from sample.model.swc_node import SwcNode
import time
import queue

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
def test3():
    start = time.time()
    tree = swcfile_to_swcnodelist(file_name="..\..\\test\data_example\ExampleTest.swc")
    # test_print_tree(tree[0])
    print(time.time() - start)

if __name__ == "__main__":
    # tree = swcfile_to_swcnodelist(file_name="..\..\\test\data_example\ExampleTest.swc")
    # test_print_tree(tree[0])
    # test3()
    pass=
