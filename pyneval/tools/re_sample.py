import queue
from pyneval.model.swc_node import SwcNode, SwcTree, Make_Virtual
from pyneval.model.euclidean_point import Line, EuclideanPoint
from anytree import PreOrderIter
from pyneval.io.swc_writer import swc_save
import copy


def itp_ok(node=None, son=None, pa=None,
           rad_mul=1.50, center_dis=None):
    '''
    judge if node can be canceled
    :param node: main node, may be deleted
    :param son: node's son
    :param pa: node's parent
    :param rad_mul:
    :param center_dis:
    :return:
    '''
    f_line = Line(e_node_1=son.get_center(), e_node_2=pa.get_center())
    e_node = node.get_center()

    foot = e_node.get_foot_point(f_line)
    if not foot.on_line(f_line):
        return False
    else:
        itp_dis = e_node.distance(foot)
        e_son = son._pos
        e_pa = pa._pos
        itp_rad = son.radius() + (pa.radius() - son.radius()) * e_son.distance(foot) / e_son.distance(e_pa)
        if center_dis is None:
            center_dis = node.radius()/2
        if node.radius() / itp_rad > rad_mul or itp_dis > center_dis:
            return False
    return True


def down_sample(swc_tree=None, rad_mul=1.50, center_dis=None, stage=0):
    stack = queue.LifoQueue()
    stack.put(swc_tree.root())
    down_pa = {}
    is_active = [True]*(max(swc_tree.id_set) + 5)

    for node in PreOrderIter(swc_tree.root()):
        if node.parent is None or node is None:
            continue
        down_pa[node] = node.parent

    while not stack.empty():
        node = stack.get()
        for son in node.children:
            stack.put(son)

        # 确保不是根节点
        if node.is_virtual() or down_pa[node].is_virtual():
            continue
        # 确保是二度节点
        if len(node.children) != 1:
            continue

        son, pa = node.children[0], down_pa[node]
        son_dis, pa_dis, grand_dis = son.parent_distance(), node.distance(down_pa[node]), son.distance(pa)

        # 确保针对采样率高的情况
        if stage == 0 and (son_dis > son.radius() + node.radius() or pa_dis > pa.radius() + node.radius()):
            continue
        if stage == 1 and (son_dis > son.radius() + node.radius() and pa_dis > pa.radius() + node.radius()):
            continue
        if itp_ok(node=node, son=son, pa=pa, rad_mul=rad_mul, center_dis=center_dis):
            is_active[node.get_id()] = False
            down_pa[son] = down_pa[node]

    return down_pa, is_active


def down_sample_swc_tree_command_line(swc_tree, config=None):
    rad_mul = config['rad_mul']
    center_dis = config['center_dis']
    stage = config['stage']
    return down_sample_swc_tree(swc_tree=swc_tree, rad_mul=rad_mul, center_dis=center_dis, stage=stage)


def down_sample_swc_tree(swc_tree, rad_mul=1.50, center_dis=None, stage=0):
    '''
    :param swc_tree: the tree need to delete node
    :param rad_mul: defult=1.5
    :param center_dis: defult=None
    :param stage: 0: for 2 degree node, delete if one side is two close, 1: for 2 degree node, delete if two sides are two close
    :return: swc_tree has changed in this function
    '''
    down_pa, is_activate = down_sample(swc_tree=swc_tree, rad_mul=rad_mul, center_dis=center_dis, stage=stage)
    new_swc_tree = SwcTree()
    node_list = [node for node in PreOrderIter(swc_tree.root())]
    id_node_map = {-1: new_swc_tree.root()}
    for node in node_list:
        if node.is_virtual():
            continue
        if is_activate[node.get_id()]:
            tmp_node = SwcNode()
            tmp_node._id = node.get_id()
            tmp_node._type = node._type
            tmp_node._pos = copy.copy(node._pos)
            tmp_node._radius = node._radius
            pa = id_node_map[down_pa[node].get_id()]
            tmp_node.parent = pa
            id_node_map[node.get_id()] = tmp_node
            new_swc_tree.id_set.add(tmp_node._id)
    return new_swc_tree


def re_sample(swc_tree, son, pa, length_threshold):
    '''
    self recursive function, add node on the middle of edge son, pa
    :param swc_tree:
    :param son:
    :param pa:
    :param length_threshold: control how many nodes to add
    :param tiff_file: optional, adjust to fit tiff if exist
    :return: True/False, it dose not matter
    '''
    dis = son.distance(pa)
    if dis - (son.radius() + pa.radius()) < length_threshold:
        return False

    new_pos = EuclideanPoint(center=[(son.get_x() + pa.get_x()) / 2,
                                     (son.get_y() + pa.get_y()) / 2,
                                     (son.get_z() + pa.get_z()) / 2])

    new_node = SwcNode(center=new_pos)
    new_node.set_r((son.radius() + pa.radius()) / 2)
    new_node._type = 7

    swc_tree.unlink_child(son)
    if not swc_tree.add_child(pa, new_node):
        raise Exception("[Error: ] add child fail type of pa :{}, type of son".format(type(pa, new_node)))
    if not swc_tree.link_child(new_node, son):
        raise Exception("[Error: ] add child fail type of pa :{}, type of son".format(type(new_node, son)))

    re_sample(swc_tree=swc_tree, son=new_node, pa=pa, length_threshold=length_threshold)
    re_sample(swc_tree=swc_tree, son=son, pa=new_node, length_threshold=length_threshold)
    return True


def up_sample_swc_tree_command_line(swc_tree, config=None):
    length_threshold = float(config['length_threshold'])
    return up_sample_swc_tree(swc_tree=swc_tree, length_threshold=length_threshold)


def up_sample_swc_tree(swc_tree, length_threshold=1.0):
    '''
    :param swc_tree: the tree need to add node(dense)
    :param length_threshold: control how many nodes to add
    :return: swc_tree has changed in this function
    '''
    up_sampled_swc_tree = swc_tree.get_copy()

    swc_list = up_sampled_swc_tree.get_node_list()
    for node in swc_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue

        re_sample(swc_tree=up_sampled_swc_tree, son=node, pa=node.parent,
                  length_threshold=length_threshold)

    # 're_sample' will change the structure of the tree. Update is required after using
    up_sampled_swc_tree.get_node_list(update=True)
    return up_sampled_swc_tree


if __name__ == "__main__":
    file_name = "6144_12288_17664"
    swc_tree = SwcTree()
    swc_tree.load("D:\\02_project\\00_neural_tracing\\01_project\PyNeval\data\swc_cut_data\\{}.swc".format(file_name))
    up_sampled_swc_tree = up_sample_swc_tree(swc_tree=swc_tree, length_threshold=1.0)
    # up_sampled_swc_tree = down_sample_swc_tree(swc_tree=swc_tree)
    swc_save(up_sampled_swc_tree, "D:\\02_project\\00_neural_tracing\\01_project\PyNeval\output\\resample\\{}.swc".format(file_name))
