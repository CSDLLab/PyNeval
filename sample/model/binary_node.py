RIGHT = "right"
LEFT = "left"
DEFULT = "DEFULT"

class BinaryNode(object):
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
                 side=DEFULT,
                 max_dep=0,
                 hight=0,
                 treesize=1,
                 leaves=1):
        self.data=data
        self.parent=parent
        self.left_son=left_son
        self.right_son=right_son
        self.side=side
        self.max_dep=max_dep
        self.hight=hight
        self.treesize=treesize
