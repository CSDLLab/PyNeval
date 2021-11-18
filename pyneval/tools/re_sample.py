import queue
import numpy as np
from pyneval.model.swc_node import SwcNode
from pyneval.model.swc_tree import SwcTree, Make_Virtual
from pyneval.model.euclidean_point import Line, EuclideanPoint
from anytree import PreOrderIter
from pyneval.pyneval_io.swc_io import swc_save
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


def down_sample(swc_tree=None, rad_mul=1.50, center_dis=None, stage=0, k=1.0):
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
        if stage == 0 and (son_dis > k*(son.radius() + node.radius()) or pa_dis > k*(pa.radius() + node.radius())):
            continue
        if stage == 1 and (son_dis > k*(son.radius() + node.radius()) and pa_dis > k*(pa.radius() + node.radius())):
            continue
        if itp_ok(node=node, son=son, pa=pa, rad_mul=rad_mul, center_dis=center_dis):
            is_active[node.get_id()] = False
            down_pa[son] = down_pa[node]

    return down_pa, is_active


def down_sample_swc_tree_command_line(swc_tree, config=None):
    rad_mul = config['rad_mul']
    center_dis = config['center_dis']
    stage = config['stage']
    return down_sample_swc_tree_stage(swc_tree=swc_tree, rad_mul=rad_mul, center_dis=center_dis, stage=stage)


def down_sample_swc_tree_stage(swc_tree, rad_mul=1.50, center_dis=None, stage=0, k=1.0):
    '''
    :param swc_tree: the tree need to delete node
    :param rad_mul: defult=1.5
    :param center_dis: defult=None
    :param stage: 0: for 2 degree node, delete if one side is too close, 1: for 2 degree node, delete if two sides are two close
    :return: swc_tree has changed in this function
    '''
    down_pa, is_activate = down_sample(swc_tree=swc_tree, rad_mul=rad_mul, center_dis=center_dis, stage=stage, k=k)
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


def down_sample_swc_tree(swc_tree, rad_mul=1.50, center_dis=None, k=1.0):
    res1 = down_sample_swc_tree_stage(swc_tree, rad_mul=rad_mul, center_dis=center_dis, stage=1, k=k)
    res2 = down_sample_swc_tree_stage(res1, rad_mul=rad_mul, center_dis=center_dis, stage=0, k=k)
    return res2


def up_sample_swc_tree_command_line(swc_tree, config=None):
    length_threshold = float(config['length_threshold'])
    return up_sample_swc_tree(swc_tree=swc_tree, length_threshold=length_threshold)


def up_sample_swc_tree(swc_tree, length_threshold):
    '''
    :param swc_tree: the tree need to upsample
    :param length_threshold: the distance between upsampled adjacent nodes.
                             floor(length_of_length/threshold - 1) new nodes will be interpolated in to an edge.
                             if length_of_length < threshold, no new nodes will be added.
    :return: upsampled swc tree
    '''
    up_sampled_swc_tree = swc_tree.get_copy()
    node_list = up_sampled_swc_tree.get_node_list()
    for node in node_list:
        # actually only div_num - 1 new nodes will be interpolated, id from 1 to div_num-1
        div_num = int(np.floor(node.parent_distance() / length_threshold))
        pa = node.parent
        cur_node = node
        for i in range(1, div_num):
            new_pos = EuclideanPoint(center=[node.get_x() + (pa.get_x() - node.get_x())/div_num*i,
                                             node.get_y() + (pa.get_y() - node.get_y())/div_num*i,
                                             node.get_z() + (pa.get_z() - node.get_z())/div_num*i])

            new_node = SwcNode(center=new_pos)
            new_node.set_r(node.radius() + (pa.radius() - node.radius())/div_num*i)
            new_node._type = 7

            up_sampled_swc_tree.unlink_child(cur_node)
            if not up_sampled_swc_tree.add_child(pa, new_node):
                raise Exception("[Error: ] add child fail type of pa :{}, type of son".format(type(pa, new_node)))
            if not up_sampled_swc_tree.link_child(new_node, cur_node):
                raise Exception("[Error: ] add child fail type of pa :{}, type of son".format(type(new_node, node)))
            cur_node = new_node
    up_sampled_swc_tree.get_node_list(update=True)
    return up_sampled_swc_tree
