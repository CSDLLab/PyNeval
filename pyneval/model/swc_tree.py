# bennieHan 2019-11-12 16:01
# all right reserved
import copy
import math
import os
import bisect
import queue

import numpy as np
from anytree import NodeMixin, RenderTree, iterators
from pyneval.model.euclidean_point import EuclideanPoint
from pyneval.model import swc_node


def Make_Virtual():
    return swc_node.SwcNode(nid=-1, center=EuclideanPoint(center=[0, 0, 0]))


def get_nearby_swc_node_list(gold_node, test_kdtree, test_pos_node_dict, threshold):
    """
    find all nodes in "test_swc_list" which are close enough to "gold_node"
    sort them by distance

    :param gold_node: swc_node
    :param test_swc_list:
    :param threshold:
    :return:
    """
    if gold_node.is_virtual():
        return
    tmp_list = []
    # find the closest pos for gold node
    target_pos_list = test_kdtree.search_knn(list(gold_node.get_center_as_tuple()), k=5)
    for pos in target_pos_list:
        target_node = test_pos_node_dict[tuple(pos[0].data)]
        if target_node.is_virtual() or gold_node.is_virtual():
            continue
        # only if gold and test nodes are very close(dis < 0.03), they can be considered as the same pos
        if gold_node.distance(target_node) < threshold:
            tmp_list.append(tuple([target_node, target_node.distance(gold_node)]))

    tmp_list.sort(key=lambda x: x[1])
    res_list = []
    for tu in tmp_list:
        res_list.append(tu[0])
    return res_list


class SwcTree:
    """A class for representing one or more SWC trees.
    For simplicity, we always assume that the root is a virtual node.
    """

    def __init__(self):
        self._root = Make_Virtual()
        self._size = None
        self._total_length = None
        self._name = None

        self.id_set = set()
        self.depth_array = None
        self.LOG_NODE_NUM = None
        self.lca_parent = None
        self.node_list = None
        self.id_node_dict = None

    def root(self):
        return self._root

    def size(self):
        self._size = len(self.id_set)
        return self._size

    def name(self):
        return self._name

    def clear(self):
        self._root = Make_Virtual()

    # warning: slow, don't use in loop
    def node_from_id(self, nid):
        niter = iterators.PreOrderIter(self._root)
        for tn in niter:
            if tn.get_id() == nid:
                return tn
        return None

    def load_list(self, lines):
        self.clear()
        nodeDict = dict()
        for line in lines:
            if not self.is_comment(line):
                #                     print line
                data = list(map(float, line.split()))
                #                     print(data)
                if len(data) == 7:
                    nid = int(data[0])
                    ntype = int(data[1])
                    pos = EuclideanPoint(center=data[2:5])
                    radius = data[5]
                    parentId = data[6]
                    if nid in self.id_set:
                        raise Exception("[Error: SwcTree.load]Same id {}".format(nid))
                    self.id_set.add(nid)
                    tn = swc_node.SwcNode(nid=nid, ntype=ntype, radius=radius, center=pos)
                    nodeDict[nid] = (tn, parentId)

        for _, value in nodeDict.items():
            tn = value[0]
            parentId = value[1]
            if parentId == -1:
                tn.parent = self._root
            else:
                if parentId not in nodeDict.keys():
                    raise Exception("[Error: SwcTree.load]Unknown parent id {}".format(parentId))
                parentNode = nodeDict.get(parentId)
                if parentNode:
                    tn.parent = parentNode[0]

        for node in self.get_node_list():
            if node.parent is None:
                continue
            if node.parent.get_id() == -1:
                node._depth = 0
            else:
                node._depth = node.parent._depth + 1
                node.root_length = node.parent.root_length + node.parent_distance()

    def load(self, path):
        self.clear()
        self._name = os.path.basename(path)
        with open(path, "r") as fp:
            lines = fp.readlines()
            self.load_list(lines)

    # def scale(self, sx, sy, sz, adjusting_radius=True):
    #     niter = iterators.PreOrderIter(self._root)
    #     for tn in niter:
    #         tn.scale(sx, sy, sz, adjusting_radius)

    def rescale(self, scale):
        for node in self.get_node_list():
            node.set_z(node.get_z() * scale[2])
            node.set_y(node.get_y() * scale[1])
            node.set_x(node.get_x() * scale[0])

    def length(self, force_update=False):
        if self._total_length is not None and force_update == False:
            return self._total_length

        node_list = self.get_node_list()
        result = 0
        for tn in node_list:
            if tn.is_virtual() or tn.parent.is_virtual():
                continue
            result += tn.parent_distance()

        return result

    def get_depth_array(self, node_num):
        self.depth_array = [0] * (node_num + 10)
        node_list = self.get_node_list()
        for node in node_list:
            self.depth_array[node.get_id()] = node.depth()

    # initialize LCA data structure in swc_tree
    def get_lca_preprocess(self, node_num=-1):
        if node_num == -1:
            node_num = self.size()
        self.get_depth_array(node_num)
        self.LOG_NODE_NUM = math.ceil(math.log(node_num, 2)) + 1
        self.lca_parent = np.zeros(shape=(node_num + 10, self.LOG_NODE_NUM), dtype=int)
        tree_node_list = self.get_node_list()

        for node in tree_node_list:
            if node.is_virtual():
                continue
            self.lca_parent[node.get_id()][0] = node.parent.get_id()
        for k in range(self.LOG_NODE_NUM - 1):
            for v in range(1, node_num + 1):
                if self.lca_parent[v][k] < 0:
                    self.lca_parent[v][k + 1] = -1
                else:
                    self.lca_parent[v][k + 1] = self.lca_parent[int(self.lca_parent[v][k])][k]
        return True

    # input node id of two swc_node, calculate LCA
    def get_lca(self, u, v):
        lca_parent = self.lca_parent
        LOG_NODE_NUM = self.LOG_NODE_NUM
        depth_array = self.depth_array

        if depth_array[u] > depth_array[v]:
            u, v = v, u
        for k in range(LOG_NODE_NUM):
            if depth_array[v] - depth_array[u] >> k & 1:
                v = lca_parent[v][k]
        if u == v:
            return u
        for k in range(LOG_NODE_NUM - 1, -1, -1):
            if lca_parent[u][k] != lca_parent[v][k]:
                u = lca_parent[u][k]
                v = lca_parent[v][k]
        return lca_parent[u][0]

    def align_roots(self, gold_tree, matches, DEBUG=False):
        offset = EuclideanPoint()
        stack = queue.LifoQueue()
        swc_test_list = self.get_node_list()

        for root in gold_tree.root().children:
            gold_anchor = np.array(root._pos)
            if root in matches.keys():
                test_anchor = np.array(matches[root]._pos)
            else:
                nearby_nodes = get_nearby_swc_node_list(
                    gold_node=root, test_swc_list=swc_test_list, threshold=root.radius() / 2
                )
                if len(nearby_nodes) == 0:
                    continue
                test_anchor = nearby_nodes[0]._pos

            offset._pos = (test_anchor - gold_anchor).tolist()
            if DEBUG:
                print ("off_set:x = {}, y = {}, z = {}".format(offset._pos[0], offset._pos[1], offset._pos[2]))

            stack.put(root)
            while not stack.empty():
                node = stack.get()
                if node.is_virtual():
                    continue

                node._pos[0] += offset._pos[0]
                node._pos[1] += offset._pos[1]
                node._pos[2] += offset._pos[2]

                for son in node.children:
                    stack.put(son)

    def change_root(self, new_root_id):
        stack = queue.LifoQueue()
        swc_list = self.get_node_list()
        list_size = max(self.id_set)
        vis_list = np.zeros(shape=(list_size + 10))
        pa_list = [None] * (list_size + 10)

        for node in swc_list:
            pa_list[node.get_id()] = node.parent
        new_root = self.node_from_id(new_root_id)

        stack.put(new_root)
        pa_list[new_root_id] = self.root()
        while not stack.empty():
            cur_node = stack.get()
            vis_list[cur_node.get_id()] = True
            for son in cur_node.children:
                if not vis_list[son.get_id()]:
                    stack.put(son)
                    pa_list[son.get_id()] = cur_node
            if (
                cur_node.parent is not None
                and cur_node.parent.get_id() != -1
                and not vis_list[cur_node.parent.get_id()]
            ):
                stack.put(cur_node.parent)
                pa_list[cur_node.parent.get_id()] = cur_node

        for i in range(1, len(swc_list)):
            swc_list[i].parent = None
        for i in range(1, len(swc_list)):
            swc_list[i].parent = pa_list[swc_list[i].get_id()]

    def type_clear(self, col=0, rt_color=2):
        node_list = self.get_node_list()
        for node in node_list:
            node._type = col
        for root in self.root().children:
            root._type = rt_color

    def radius_limit(self, x):
        node_list = self.get_node_list()
        for node in node_list:
            node._radius /= x

    def next_id(self):
        return max(self.id_set) + 1

    # use this function if son is a new node
    def add_child(self, node, son_node):
        # swc_node is a module in model, while node and son_node are objects.
        if not isinstance(son_node, swc_node.SwcNode) or not isinstance(node, swc_node.SwcNode):
            return False
        nid = self.next_id()

        son_node.set_id(nid)
        son_node.parent = node

        self.id_set.add(nid)
        return True

    # use this function if son use to be a part of this tree
    def link_child(self, pa, son):
        if not isinstance(pa, swc_node.SwcNode) or not isinstance(son, swc_node.SwcNode):
            return False
        son.parent = pa
        return True

    def remove_node(self, node):
        if not isinstance(node, swc_node.SwcNode):
            return False
        pa = node.parent
        children = list(pa.children)
        children.remove(node)
        pa.children = tuple(children)

        for son in node.children:
            son.parent = self._root
        self.id_set.remove(node.get_id())
        return True

    def unlink_child(self, node):
        if not isinstance(node, swc_node.SwcNode):
            return False
        pa = node.parent
        children = list(pa.children)
        children.remove(node)
        pa.children = tuple(children)
        node.parent = self.root()
        return True

    def get_node_list(self, update=False):
        if self.node_list is None or update:
            self.node_list = []
            q = queue.LifoQueue()
            q.put(self._root)
            while not q.empty():
                cur = q.get()
                self.node_list.append(cur)
                for child in cur.children:
                    q.put(child)

        return self.node_list

    def sort_node_list(self, key="id"):
        """
        index:
            default: order by pre order
            id: order by id
            compress: re-order from 1 to the size of swc tree
        """
        if key == "default":
            self.get_node_list(update=True)
        if key == "id":
            self.node_list.sort(key=lambda node: node.get_id())
        if key == "compress":
            self.node_list.sort(key=lambda node: node.get_id())
            id_list = []
            for id in self.id_set:
                id_list.append(id)
            id_list.sort()
            for node in self.node_list:
                if node.is_virtual():
                    continue
                new_id = bisect.bisect_left(id_list, node.get_id()) + 1
                self.id_set.remove(node.get_id())
                self.id_set.add(new_id)
                node.set_id(new_id)

    def to_str_list(self):
        swc_node_list = self.get_node_list()
        swc_str = []
        for node in swc_node_list:
            if node.is_virtual():
                continue
            swc_str.append(node.to_swc_str())
        return "".join(swc_str)

    def get_copy(self):
        new_tree = SwcTree()
        swc_str = self.to_str_list().split("\n")
        new_tree.load_list(swc_str)
        return new_tree

    def get_id_node_dict(self):
        if self.id_node_dict is not None:
            return self.id_node_dict
        self.id_node_dict = {}
        for node in self.get_node_list():
            self.id_node_dict[node.get_id()] = node
        return self.id_node_dict

    def get_branch_swc_list(self):
        """
        get branch nodes (link to more than 3 nodes) of swc tree
        """
        swc_list = self.get_node_list()
        branch_list = []
        for node in swc_list:
            if node.is_virtual():
                continue
            if node.parent.is_virtual():
                if len(node.children) > 2:
                    branch_list.append(node)
            elif len(node.children) > 1:
                branch_list.append(node)
        return branch_list

    def get_leaf_swc_list(self):
        swc_list = self.get_node_list()
        leaf_list = []
        for node in swc_list:
            if node.is_virtual():
                continue
            if node.parent.is_virtual():
                if len(node.children) == 1:
                    leaf_list.append(node)
            if len(node.children) == 0:
                leaf_list.append(node)
        return leaf_list

    def set_node_type_by_topo(self, root_id=1):
        """
        root_id decide other nodes' id
        branch = root_id + 1
        leaf = root_id + 3
        normal node = root_id + 2
        """
        swc_list = self.get_node_list()
        for node in swc_list:
            if node.is_virtual():
                continue
            if node.parent.get_id() == -1:
                node._type = root_id
            elif len(node.children) > 1:
                node._type = root_id + 1
            elif len(node.children) == 1:
                node._type = root_id + 2
            else:
                node._type = root_id + 3

    def break_branches(self):
        breaked_tree = self.get_copy()
        branch_list = breaked_tree.get_branch_swc_list()
        for branch in branch_list:
            if branch.is_virtual():
                continue
            for branch_son in branch.children:
                breaked_tree.unlink_child(branch_son)
            # breaked_tree.unlink_child(branch)
        breaked_tree.get_node_list(update=True)
        return breaked_tree

    def is_comment(self, line):
        return line.strip().startswith("#")

    # warning: slow, don't use in loop
    def parent_id(self, nid):
        tn = self.node_from_id(nid)
        return tn.get_parent_id() if tn else None

    # warning: slow, don't use in loop
    def parent_node(self, nid):
        tn = self.node_from_id(nid)
        return tn.parent if tn else None

    # warning: slow, don't use in loop
    def child_list(self, nid):
        tn = self.node_from_id(nid)
        return tn.children if tn else None

    # warning: slow, don't use in loop
    def radius(self, nid):
        return self.node_from_id(nid).radius()

if __name__ == "__main__":
    tree = SwcTree()
    tree.load("E:\\04_code\\00_neural_reconstruction\PyNeval\data\std_test_data\\6656_2816_22016\\6656_2816_22016_gold.swc")
    b_tree = tree.break_branches()
    from pyneval.pyneval_io import swc_io
    swc_io.swc_save(b_tree, "E:\\04_code\\00_neural_reconstruction\PyNeval\data\std_test_data\\6656_2816_22016\\6656_2816_22016_gold_b.swc")