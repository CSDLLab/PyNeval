import unittest
from pymets.metric.utils.edge_match_utils import is_route_clean, get_edge_rtree, get_idedge_dict
from pymets.model.swc_node import SwcTree, SwcNode
from pymets.model.euclidean_point import EuclideanPoint, Line


class TestGetLcaLength(unittest.TestCase):
    test_swc_tree = SwcTree()
    test_rtree = None
    id_edge_dict = None

    def init(self):
        self.test_swc_tree.load("../../data_example/unit_test/get_nearby_edges_tree1.swc")
        self.test_rtree = get_edge_rtree(self.test_swc_tree)
        self.id_edge_dict = get_idedge_dict(self.test_swc_tree)

        self.test_swc_tree.get_lca_preprocess()

    def test_1(self):
        line_tuple_a = tuple([self.test_swc_tree.node_from_id(8),
                              self.test_swc_tree.node_from_id(7)])
        line_tuple_b = tuple([self.test_swc_tree.node_from_id(7),
                              self.test_swc_tree.node_from_id(6)])
        e_node1 = EuclideanPoint(center=[1.03, -2.1, 6.31])
        e_node2 = EuclideanPoint(center=[3.87, 0.98, 1.17])

        # ans = is_route_clean(gold_swc_tree=self.test_swc_tree,
        #                    gold_line_tuple_a=line_tuple_a,
        #                    gold_line_tuple_b=line_tuple_b,
        #                    node1, node2,
        #                    edge_use_dict, vis_list,
        #                    DEBUG):

