import queue
import kdtree
from anytree import PreOrderIter
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.config_utils import get_default_threshold
from pyneval.metric.utils.config_utils import SAME_POS_TH


def create_kdtree(node_list):
    """
    construct a kd-tree using nodes in the node list.
    Args:
        node_list(List): a list of Swc Nodes
    Return:
        my_kdtree(KD tree)
        pos_node_dict(Dict):
            key: tuple of (x, y, z) coordinate
            value: Swc node corresponds to the key's position
    """
    pos_node_dict = {}
    center_list = []

    for node in node_list:
        if node.is_virtual():
            continue
        pos_node_dict[node.get_center_as_tuple()] = node
        center_list.append(list(node.get_center_as_tuple()))
    my_kdtree = kdtree.create(center_list)
    return my_kdtree, pos_node_dict


def get_swc2swc_dicts(src_node_list, tar_node_list):
    '''
    get a dict mapping nodes from the source node list to the target node list
    two nodes are mapped if they are on the exactly same position (dis < SAME_POS_TH)
    Args:
        src_node_list(List): a list of Swc Nodes. find a match for each node in this list if possible.
        tar_node_list(List): a list of Swc Nodes. for src node list to search for matching target.
    Return:
        src_tar_dict(Dict):
            keys: node in src
            value: node in tar
    '''
    target_kd, pos_node_dict = create_kdtree(tar_node_list)

    src_tar_dict = {}

    for src_node in src_node_list:
        if src_node.is_virtual():
            continue
        # find the closest pos for gold node
        target_pos = target_kd.search_knn(list(src_node.get_center_as_tuple()), k=1)[0]
        target_node = pos_node_dict[tuple(target_pos[0].data)]
        # only if gold and test nodes are very close(dis < 0.03), they can be considered as the same pos
        if src_node.distance(target_node) < SAME_POS_TH:
            src_tar_dict[src_node] = target_node
        else:
            src_tar_dict[src_node] = None

    return src_tar_dict


if __name__ == "__main__":
    pass