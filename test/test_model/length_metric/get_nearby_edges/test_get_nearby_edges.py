import unittest
from pyneval.metric.utils.edge_match_utils import get_nearby_edges, get_edge_rtree, get_idedge_dict
from pyneval.model.swc_node import SwcTree, SwcNode
from pyneval.model.euclidean_point import EuclideanPoint


class TestGetNearbyEdges(unittest.TestCase):
    test_swc_tree = SwcTree()
    test_rtree = None
    id_edge_dict = None

    def init(self):
        self.test_swc_tree.load("../../data_example/unit_test/get_nearby_edges_tree1.swc")
        self.test_rtree = get_edge_rtree(self.test_swc_tree)
        self.id_edge_dict = get_idedge_dict(self.test_swc_tree)

    def test_1(self):
        line = [[7, 6], [8, 7]]
        dis = [0.009317785645644346, 0.07576191838507501]

        self.init()
        e_point = EuclideanPoint(center=[5, -2.7, 4.8])
        point = SwcNode(center=e_point)
        threshold = 0.1

        res = get_nearby_edges(self.test_rtree, point, self.id_edge_dict, threshold, False, DEBUG=False)
        self.assertEqual(len(res), 2)

        for i in range(len(res)):
            element = res[i]
            self.assertEqual(element[0][0].get_id(), line[i][0])
            self.assertEqual(element[0][1].get_id(), line[i][1])
            self.assertEqual(element[1], dis[i])

    def test_2(self):
        line = [[7, 6], [8, 7]]
        dis = [0.009317785645644346, 0.07576191838507501]

        self.init()
        e_point = EuclideanPoint(center=[5.02439, -2.75148, 4.84998])
        point = SwcNode(center=e_point)
        threshold = 0.1

        res = get_nearby_edges(self.test_rtree, point, self.id_edge_dict, threshold, True, DEBUG=False)
        print(res.__str__())
        self.assertEqual(len(res), 0)


if __name__ == "__main__":
    unittest.main()


