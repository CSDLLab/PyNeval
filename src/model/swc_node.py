# bennieHan 2019-11-12 16:01
# all right reserved
import math
from anytree import NodeMixin, iterators, RenderTree
_3D = "3d"
_2D = "2d"

def Make_Virtual():
    return SwcNode(nid=-1)


def compute_platform_area(r1, r2, h):
    return (r1 + r2) * h * math.pi


# to test
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


# to test
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


class SwcNode(NodeMixin):
    """
        this is a class that temporarily store SWC file
        Attributes:
        id: id of the node,
        type: leaf = 1,continuation = 2, bifurcation = 3,
        parent: pa node id,
        son=[]: son list,
        x: x coordinate,
        y: y coordinate,
        z: z coordinate,
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
                 radius=1,
                 center=[0, 0, 0],
                 parent=None,

                 surface_area=0.0,
                 volume=0.0,

                 parent_trajectory=None,
                 left_trajectory=None,
                 right_trajectory=None,

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

        self.parent_trajectory=parent_trajectory
        self.left_trajectory=left_trajectory
        self.right_trajectory=right_trajectory

        self.path_length=path_length
        self.xy_path_length=xy_path_length
        self.z_path_length=z_path_lenth

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

    def get_id(self):
        """Returns the ID of the node.
        """
        return self._id

    def distance(self, tn = None, mode = _3D):
        """ Returns the distance to another node.
        It returns 0 if either of the nodes is not regular.

        Args:
          tn : the target node for distance measurement
        """
        if tn is None:
            return None

        if tn and self.is_regular() and tn.is_regular():
            dx = self._pos[0] - tn._pos[0]
            dy = self._pos[1] - tn._pos[1]
            dz = self._pos[2] - tn._pos[2]
            if mode == _2D:
                dz = 0.0
            d2 = dx * dx + dy * dy + dz * dz

            return math.sqrt(d2)

        return 0.0

    def parent_distance(self):
        """ Returns the distance to it parent.
        """
        return self.distance(self.parent)

    def radius(self):
        return self._radius

    def scale(self, sx, sy, sz, adjusting_radius=True):
        """Transform a node by scaling
        """

        self._pos[0] *= sx
        self._pos[1] *= sy
        self._pos[2] *= sz

        if adjusting_radius:
            self._radius *= math.sqrt(sx * sy)

    def to_swc_str(self):
        return '%d %d %g %g %g %g' % (self._id, self._type, self._pos[0], self._pos[1], self._pos[2], self._radius)

    def get_parent_id(self):
        return -2 if self.is_root else self.parent.get_id()

    def __str__(self):
        return '%d (%d): %s, %g' % (self._id, self._type, str(self._pos), self._radius)


class SwcTree:
    """A class for representing one or more SWC trees.
    For simplicity, we always assume that the root is a virtual node.
    """

    def __init__(self):
        self._root = Make_Virtual()

    def _print(self):
        print(RenderTree(self._root).by_attr("_id"))

    def clear(self):
        self._root = Make_Virtual()

    def is_comment(self, line):
        return line.strip().startswith('#')

    def root(self):
        return self._root

    def regular_root(self):
        return self._root.children

    def node_from_id(self, nid):
        niter = iterators.PreOrderIter(self._root)
        for tn in niter:
            if tn.get_id() == nid:
                return tn
        return None

    def parent_id(self, nid):
        tn = self.node_from_id(nid)
        if tn:
            return tn.get_parent_id()

    def parent_node(self, nid):
        tn = self.node_from_id(nid)
        if tn:
            return tn.parent

    def child_list(self, nid):
        tn = self.node_from_id(nid)
        if tn:
            return tn.children

    def load(self, path):
        self.clear()
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
                        pos = data[2:5]
                        radius = data[5]
                        parentId = data[6]
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

    def save(self, path):
        with open(path, 'w') as fp:
            niter = iterators.PreOrderIter(self._root)
            for tn in niter:
                if tn.is_regular():
                    fp.write('%s %d\n' % (tn.to_swc_str(), tn.get_parent_id()))
            fp.close()

    def has_regular_node(self):
        return len(self.regular_root()) > 0

    #     def max_id(self):
    #         for node in
    #         nodes = self._tree.nodes()
    #         return max(nodes)

    def node_count(self, regular=True):
        count = 0
        niter = iterators.PreOrderIter(self._root)
        for tn in niter:
            if regular:
                if tn.is_regular():
                    count += 1
            else:
                count += 1

        return count

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

    def length(self):
        niter = iterators.PreOrderIter(self._root)
        result = 0
        for tn in niter:
            result += tn.parent_distance()

        return result

    def radius(self, nid):
        return self.node(nid).radius()


if __name__ == '__main__':
    print('testing ...')

    tn1 = SwcNode(nid=1, radius=1, center=[0, 0, 0])
    tn2 = SwcNode(nid=1, radius=1, center=[0, 0, 2], parent=tn1)
    print(compute_two_node_area(tn1, tn2, 0.5))
    print(compute_surface_area(tn1, 2.0))

    tn = Make_Virtual()
    print(tn.get_id())
    print(tn.get_parent_id())
    print("children:{}".format(tn.children))
    print(list(tn.children))

    tn1 = SwcNode(nid=1, parent=tn)
    print(tn1.get_parent_id())
    print(tn.children)

    swc = SwcTree()
    swc.load('D:\gitProject\mine\PyMets\\test\data_example\gold\ExampleGoldStandard.swc')
    swc._print()
    swc.save('D:\gitProject\mine\PyMets\\test\data_example\gold\ExampleGoldStandard.swc')
    print(swc.node_count(False))

    print(swc.root())
    tn = swc.node_from_id(2)
    print(tn)
    print(swc.has_regular_node())
    #     print(swc.max_id())
    print(swc.node_count())
    print(tn.parent_distance())
    swc.scale(2, 2, 2)
    print(tn.parent_distance())
    # #     swc.save('/Users/zhaot/Work/neutube/neurolabi/data/test.swc')
    print(swc.length())

    #     print(swc.compute_surface_area(tn, 2))

    swc.clear()
    swc._print()

    tn = SwcNode(nid=1, radius=1, parent=swc.root())
    swc._print()
#     print(swc.compute_surface_area(tn, 2))