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
                 id=-1,
                 type=0,
                 parent=-1,
                 son=[],
                 x=0.0,
                 y=0.0,
                 z=0.0,
                 radius=0.0,
                 surface_area=0.0,
                 volume=0.0,

                 parent_trajectory=0.0,
                 left_trajectory=0.0,
                 right_trajectory=0.0,

                 path_length=0.0,
                 xy_path_length=0.0,
                 z_path_lenth=0.0):
        self.id = id
        self.type = type
        self.parent = parent
        self.son = son
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
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