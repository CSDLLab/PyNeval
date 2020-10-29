import queue
import kdtree
from anytree import PreOrderIter
from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.config_utils import get_default_threshold
from pyneval.metric.utils.config_utils import SAME_POS_TH


# for length metric (unused)
def get_kdtree_data(kd_node):
    return kd_node[0].data


# def check_match(gold_node_knn, son_node_knn, edge_set, id_center_dict):
#     for pa in gold_node_knn:
#         test_pa_node = id_center_dict[tuple(get_kdtree_data(pa))]
#         for tpn in test_pa_node:
#             for sn in son_node_knn:
#                 test_son_node = id_center_dict[tuple(get_kdtree_data(sn))]
#                 for tsn in test_son_node:
#                     if tuple([tpn, tsn]) in edge_set:
#                         edge_set.remove(tuple([tpn, tsn]))
#                         edge_set.remove(tuple([tsn, tpn]))
#                         return tuple([tpn, tsn])
#     return None


def create_kdtree(node_list):
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
    get a dict mapping nodes from node list source to node list target
    if two nodes are mapped if they are on the same position
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


# def search_knn(kdtree, id_center_dict, gold_node, knn_num):
#     knn_pos = kdtree.search_knn(gold_node._pos, knn_num)
#     knn_node = []
#     for poses in knn_pos:
#         node_list = id_center_dict[tuple(poses)]
#         for node in node_list:
#             knn_node.append(node)
#     return knn_node[:knn_num]


if __name__ == "__main__":
    pass