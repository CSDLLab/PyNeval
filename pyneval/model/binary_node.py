from anytree import NodeMixin
from pyneval.model.euclidean_point import EuclideanPoint
import copy
import math
import queue

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

    def is_left(self):
        if self.get_side() == LEFT:
            return True
        return False

    def get_side(self):
        if self.is_root():
            return DEFULT
        if self.parent.left_son == self:
            return LEFT
        if self.parent.right_son == self:
            return RIGHT
        return LEFT

    def is_root(self):
        if self.parent == None:
            return True
        return False

    def is_leaf(self):
        if self.left_son == None and self.right_son == None:
            return True
        return False

    def to_str(self):
        print("id = {} path_length= {} xy_path_length = {} z_path_length = {}".format(
            self.data.get_id(), self.data.path_length, self.data.xy_path_length, self.data.z_path_length))
        if self.left_son is not None:
            print("left son: {}".format(self.left_son.data.get_id()))
        if self.right_son is not None:
            print("right son {}".format(self.right_son.data.get_id()))
        print("---------------------------")

    def print_tree(self):
        q = queue.LifoQueue()
        q.put(self)
        while not q.empty():
            cur = q.get()
            if cur is None:
                continue
            cur.to_str()
            q.put(cur.left_son)
            q.put(cur.right_son)

    def get_node_list(self):
        node_list = list()
        stack = queue.LifoQueue()
        stack.put(self)

        while not stack.empty():
            node = stack.get()
            node_list.append(node)
            if node.has_children():
                stack.put(node.left_son)
                stack.put(node.right_son)
        return node_list
