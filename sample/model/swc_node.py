# bennieHan 2019-11-12 16:01
# all right reserved

class SwcNode(object):
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
    """

    def __init__(self,
                 id=-1,
                 type=0,
                 parent=-1,
                 son=[],
                 x=0.0,
                 y=0.0,
                 z=0.0,
                 radius=0.0,
                 xy_parent_trajectory=0.0,
                 z_parent_trajectory=0.0,
                 parent_trajectory=0.0):
        self.id = id
        self.type = type
        self.parent = parent
        self.son = son
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.xy_parent_trajectory=xy_parent_trajectory
        self.z_parent_trajectory=z_parent_trajectory
        self.parent_trajectory=parent_trajectory