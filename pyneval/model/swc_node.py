# bennieHan 2019-11-12 16:01
# all right reserved

import math
import os
import bisect
import queue

import numpy as np
from anytree import NodeMixin, RenderTree, iterators
from pyneval.model.euclidean_point import EuclideanPoint

_3D = "3d"
_2D = "2d"


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
    print (remain_dist)

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

    def __init__(
        self,
        nid=-1,
        ntype=0,
        radius=1.0,
        center=None,
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
        z_path_lenth=0.0,
    ):
        self._id = nid
        self._type = ntype
        self.parent = parent
        self._pos = center if center is not None else EuclideanPoint(center=[0, 0, 0])
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

    def set_center(self, center: EuclideanPoint):
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
            return "{} {} {} {} {} {} {}\n".format(
                self._id, self._type, self.get_x(), self.get_y(), self.get_z(), self._radius, pid
            )

        return "{} {} {} {} {} {} {}\n".format(
            self._id, self._type, self.get_x(), self.get_y(), self.get_z(), self._radius, self.parent.get_id()
        )

    def __str__(self):
        return "%d (%d): %s, %g" % (self._id, self._type, str(self.get_center()._pos), self._radius)
