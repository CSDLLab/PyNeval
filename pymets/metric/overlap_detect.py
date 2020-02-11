from pymets.model.swc_node import SwcNode,SwcTree,Make_Virtual
from pymets.model.euclidean_point import EuclideanPoint,Line
from pymets.metric.utils.edge_match_utils import get_idedge_dict, get_edge_rtree, get_lca_length, get_nearby_edges
from anytree import PreOrderIter
from pymets.io.save_swc import swc_save
from pymets.io.read_json import read_json
import math,time


# find successful matched edge
def get_self_match_edges_e_fast(swc_tree=None,
                                dis_threshold=None, threshold_l=None, DEBUG=False):
    idx3d = get_edge_rtree(swc_tree)
    id_edge_dict = get_idedge_dict(swc_tree)
    node_list = [node for node in PreOrderIter(swc_tree.root())]

    for node in node_list:
        if node.is_virtual() or node.parent.is_virtual():
            continue
        parent = node.parent

        line_tuple_as = get_nearby_edges(idx3d, node, id_edge_dict, not_self=True)
        line_tuple_bs = get_nearby_edges(idx3d, node.parent, id_edge_dict,  not_self=True)

        done = False
        for line_tuple_a_d in line_tuple_as:
            if done:
                break
            for line_tuple_b_d in line_tuple_bs:
                line_tuple_a = line_tuple_a_d[0]
                dis_a = line_tuple_a_d[1]
                line_tuple_b = line_tuple_b_d[0]
                dis_b = line_tuple_b_d[1]

                test_length = get_lca_length(swc_tree, \
                               line_tuple_a, \
                               line_tuple_b, \
                               Line([node._pos, node.parent._pos]))
                gold_length = node.distance(parent)

                if dis_threshold == -1:
                    threshold1 = node.radius()
                    threshold2 = node.parent.radius()
                else:
                    threshold1 = dis_threshold
                    threshold2 = dis_threshold

                if threshold_l == -1:
                    threshold_tmpl = gold_length / 5
                else:
                    threshold_tmpl = threshold_l

                if dis_a <= threshold1 and dis_b <= threshold2 and \
                        math.fabs(test_length - gold_length) < threshold_tmpl:
                    if DEBUG:
                        print("node = {} test_length = {} gold_length = {}".format(
                            node.get_id(), test_length, gold_length
                        ))
                    node._type = 3
                    node.parent._type = 3
                    done = True
                    break


def overlap_detect(swc_tree, out_path, config=None):
    swc_tree.get_lca_preprocess()

    dis_threshold = config["radius_threshold"]
    length_threshold = config["length_threshold"]

    get_self_match_edges_e_fast(swc_tree=swc_tree,
                                dis_threshold=dis_threshold, threshold_l=length_threshold, DEBUG=False)
    swc_save(swc_tree, out_path)


if __name__ == '__main__':
    tree = SwcTree()
    tree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\overlap_sample5.swc")

    config = read_json("D:\gitProject\mine\PyMets\config\overlap_detect.json")
    overlap_detect(tree,
                   "../../output/overlap_sample5.swc",
                   config)