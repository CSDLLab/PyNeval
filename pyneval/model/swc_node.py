# bennieHan 2019-11-12 16:01
# all right reserved

from anytree import NodeMixin, iterators, RenderTree
from pyneval.model.euclidean_point import EuclideanPoint
import os

import math
import queue
import numpy as np
import copy

_3D = "3d"
_2D = "2d"


def Make_Virtual():
    return SwcNode(nid=-1, center=EuclideanPoint(center=[0, 0, 0]))


def get_nearby_swc_node_list(gold_node, test_kdtree, test_pos_node_dict, threshold):
    '''
    find all nodes in "test_swc_list" which are close enough to "gold_node"
    sort them by distance

    :param gold_node: swc_node
    :param test_swc_list:
    :param threshold:
    :return:
    '''
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


# not used old code
def compute_platform_area(r1, r2, h):
    return (r1 + r2) * h * math.pi


# not used old code
def compute_two_node_area(tn1, tn2, remain_dist):
    """Returns the surface area formed by two nodes
    """
    r1 = tn1.radius()
    r2 = tn2.radius()
    d = tn1.distance(tn2)
    print(remain_dist)

    if remain_dist >= d:
        h = d
    else:
        h = remain_dist
        a = remain_dist / d
        r2 = r1 * (1 - a) + r2 * a

    area = compute_platform_area(r1, r2, h)
    return area


# not used old code
def compute_surface_area(tn, range_radius):
    area = 0

    # backtrace
    currentDist = 0
    parent = tn.parent
    while parent and currentDist < range_radius:
        remainDist = range_radius - currentDist
        area += compute_two_node_area(tn, parent, remainDist)
        currentDist += tn.distance(parent)
        tn = parent
        parent = tn.parent

    # forwardtrace
    currentDist = 0
    childList = tn.children
    while len(childList) == 1 and currentDist < range_radius:
        child = childList[0]
        remainDist = range_radius - currentDist
        area += compute_two_node_area(tn, child, remainDist)
        currentDist += tn.distance(child)
        tn = child
        childList = tn.children

    return area


def get_lca(u, v):
    tmp_set = set()
    tmp_u = u
    tmp_v = v
    while u.get_id() != -1:
        tmp_set.add(u.get_id())
        u = u.parent

    while v.get_id() != -1:
        if v.get_id() in tmp_set:
            return v.get_id()
        v = v.parent
    return None


class SwcNode(NodeMixin):
    """
        this is a class that temporarily store SWC file
        Attributes:
        id: id of the node,
        type: leaf = 1,continuation = 2, bifurcation = 3,
        parent: pa node,
        son=[]: son list,
        center: Euclidean point describe node center
        radius: radius of the node
        surface_area: surface area of the cylinder, radius is current radius, length is the distance to its parent
        volume: volume of the cylinder. radious is the same as above

        parent_trajectory: distance to root
        left_trajectory: distance to the farthest son of left_son
        right_trajectory: distance to the farthest son of right_son

        path_length: distance to parent
        xy_path_length: distance to parent regardless z coordinate
        z_path_lenth: distance to parent
    """

    def __init__(self,
                 nid=-1,
                 ntype=0,
                 radius=1.0,
                 center=EuclideanPoint(center=[0,0,0]),
                 parent=None,
                 depth=0,

                 surface_area=0.0,
                 volume=0.0,

                 parent_trajectory=None,
                 left_trajectory=None,
                 right_trajectory=None,

                 route_length=0.0,
                 path_length=0.0,
                 xy_path_length=0.0,
                 z_path_lenth=0.0):
        self._id = nid
        self._type = ntype
        self.parent = parent
        self._pos = center
        self._radius = radius
        self.surface_area = surface_area
        self.volume = volume
        self._depth = depth

        self.parent_trajectory = parent_trajectory
        self.left_trajectory = left_trajectory
        self.right_trajectory = right_trajectory

        self.root_length = route_length
        self.path_length = path_length
        self.xy_path_length = xy_path_length
        self.z_path_length = z_path_lenth

    def set_id(self, id):
        self._id = id

    def get_id(self):
        return self._id

    def get_x(self):
        return self._pos.get_x()

    def get_y(self):
        return self._pos.get_y()

    def get_z(self):
        return self._pos.get_z()

    def set_x(self, x):
        self._pos.set_x(x)

    def set_y(self, y):
        self._pos.set_y(y)

    def set_z(self, z):
        self._pos.set_z(z)

    def set_r(self, r):
        self._radius = r

    def get_center(self):
        return self._pos

    def get_center_as_tuple(self):
        return tuple([round(self.get_x(), 2), round(self.get_y(), 2), round(self.get_z(), 2)])

    def set_center(self, center):
        if not isinstance(center, EuclideanPoint):
            raise Exception("[Error: ]not EuclideanPoint")
        del self._pos
        self._pos = center

    def depth(self):
        return self._depth

    def radius(self):
        return self._radius

    def get_parent_id(self):
        return -2 if self.is_root else self.parent.get_id()

    def add_length(self, swc_node):
        self.path_length += swc_node.path_length
        self.xy_path_length += swc_node.xy_path_length
        self.z_path_length += swc_node.z_path_length

    def add_data(self, swc_node):
        self.path_length += swc_node.path_length
        self.xy_path_length += swc_node.xy_path_length
        self.z_path_length += swc_node.z_path_length
        self.volume += swc_node.volume
        self.surface_area += swc_node.surface_area

    def is_virtual(self):
        """Returns True iff the node is virtual.
        """
        return self._id < 0

    def is_regular(self):
        """Returns True iff the node is NOT virtual.
        """
        return self._id >= 0

    def distance(self, tn=None, mode=_3D):
        """ Returns the distance to another node.
        It returns 0 if either of the nodes is not regular.

        Args:
          tn : the target node for distance measurement
        """
        # make sure itself is a regular node
        if not self.is_regular():
            return 0.0

        # make sure tn is a valid swc node
        if isinstance(tn, SwcNode) and tn.is_regular():
            if mode == _2D:
                return self.get_center().distance_to_point_2d(tn.get_center())
            return self.get_center().distance(tn.get_center())

        # euc node is also acceptable
        if isinstance(tn, EuclideanPoint):
            if mode == _2D:
                return self.get_center().distance_to_point_2d(tn)
            return self.get_center().distance(tn)

        return 0.0

    def parent_distance(self):
        """ Returns the distance to it parent.
        """
        return self.distance(self.parent)

    def scale(self, sx, sy, sz, adjusting_radius=True):
        """Transform a node by scaling
        """

        self._pos[0] *= sx
        self._pos[1] *= sy
        self._pos[2] *= sz

        if adjusting_radius:
            self._radius *= math.sqrt(sx * sy)

    def is_isolated(self):
        if (self.parent is None or self.parent.get_id() == -1) and len(self.children) == 0:
            return True
        return False

    def to_swc_str(self, pid=None):
        if pid is not None:
            return '{} {} {} {} {} {} {}\n'.format(
                self._id, self._type, self.get_x(), self.get_y(), self.get_z(), self._radius, pid)

        return '{} {} {} {} {} {} {}\n'.format(
            self._id, self._type, self.get_x(), self.get_y(), self.get_z(), self._radius, self.parent.get_id())

    def __str__(self):
        return '%d (%d): %s, %g' % (self._id, self._type, str(self.get_center()._pos), self._radius)


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

    def is_comment(self, line):
        return line.strip().startswith('#')

    def root(self):
        return self._root

    def size(self):
        self._size = len(self.id_set)
        return self._size

    def regular_root(self):
        return self._root.children

    def _print(self):
        print(RenderTree(self._root).by_attr("_id"))

    def clear(self):
        self._root = Make_Virtual()

    def get_name(self):
        return self._name

    # warning: slow, don't use in loop
    def node_from_id(self, nid):
        niter = iterators.PreOrderIter(self._root)
        for tn in niter:
            if tn.get_id() == nid:
                return tn
        return None

    # warning: slow, don't use in loop
    def parent_id(self, nid):
        tn = self.node_from_id(nid)
        if tn:
            return tn.get_parent_id()

    # warning: slow, don't use in loop
    def parent_node(self, nid):
        tn = self.node_from_id(nid)
        if tn:
            return tn.parent

    # warning: slow, don't use in loop
    def child_list(self, nid):
        tn = self.node_from_id(nid)
        if tn:
            return tn.children

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
                    tn = SwcNode(nid=nid, ntype=ntype, radius=radius, center=pos)
                    nodeDict[nid] = (tn, parentId)

        for _, value in nodeDict.items():
            tn = value[0]
            parentId = value[1]
            if parentId == -1:
                tn.parent = self._root
            else:
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
        with open(path, 'r') as fp:
            lines = fp.readlines()
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
                        tn = SwcNode(nid=nid, ntype=ntype, radius=radius, center=pos)
                        nodeDict[nid] = (tn, parentId)
            fp.close()

        for _, value in nodeDict.items():
            tn = value[0]
            parentId = value[1]
            if parentId == -1:
                tn.parent = self._root
            else:
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

    def has_regular_node(self):
        return len(self.regular_root()) > 0

    def parent_distance(self, nid):
        d = 0
        tn = self.node(nid)
        if tn:
            parent_tn = tn.parent
            if parent_tn:
                d = tn.distance(parent_tn)

        return d

    def scale(self, sx, sy, sz, adjusting_radius=True):
        niter = iterators.PreOrderIter(self._root)
        for tn in niter:
            tn.scale(sx, sy, sz, adjusting_radius)

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

    def radius(self, nid):

        return self.node(nid).radius()

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
                nearby_nodes = get_nearby_swc_node_list(gold_node=root, test_swc_list=swc_test_list,
                                                        threshold=root.radius() / 2)
                if len(nearby_nodes) == 0:
                    continue
                test_anchor = nearby_nodes[0]._pos

            offset._pos = (test_anchor - gold_anchor).tolist()
            if DEBUG:
                print("off_set:x = {}, y = {}, z = {}".format(
                    offset._pos[0], offset._pos[1], offset._pos[2]))

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
        vis_list = np.zeros(shape=(list_size+10))
        pa_list = [None] * (list_size+10)

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
            if cur_node.parent is not None and \
                    cur_node.parent.get_id() != -1 and \
                    not vis_list[cur_node.parent.get_id()]:
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
    def add_child(self, swc_node, swc_son_node):
        if not isinstance(swc_son_node, SwcNode) or not isinstance(swc_node, SwcNode):
            return False
        nid = self.next_id()

        swc_son_node.set_id(nid)
        swc_son_node.parent = swc_node

        self.id_set.add(nid)
        return True

    # use this function if son use to be a part of this tree
    def link_child(self, pa, son):
        if not isinstance(pa, SwcNode) or not isinstance(son, SwcNode):
            return False
        son.parent = pa
        return True

    def remove_node(self, node):
        if not isinstance(node, SwcNode):
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
        if not isinstance(node, SwcNode):
            return False
        pa = node.parent
        children = list(pa.children)
        children.remove(node)
        pa.children = tuple(children)
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

    def sort_node_list(self, key="default"):
        '''
        index:
            default: order by pre order
            id: order by id
        '''
        if key == "default":
            self.get_node_list(update=True)
        if key == "id":
            self.node_list.sort(key=lambda node:node.get_id())

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


if __name__ == '__main__':
    import os
    from pyneval.io.swc_writer import swc_save
    path = "..\..\data\\test_data\\topo_metric_data"
    for file in os.listdir(path):
        tree = SwcTree()
        tree.load(os.path.join(path, file))
        if file[:4] == "gold":
            tree.set_node_type_by_topo(root_id=1)
        else:
            tree.set_node_type_by_topo(root_id=5)
        swc_save(tree, out_path=os.path.join(path, "s" + file))

