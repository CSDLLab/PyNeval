import unittest
import numpy as np
from pyneval.metric.utils.edge_match_utils import get_idedge_dict, get_edge_rtree, get_nearby_edges
from pyneval.model.swc_node import SwcTree,SwcNode
from pyneval.model.euclidean_point import EuclideanPoint,Line
from rtree import index


# 获取线段的bounding box
def get_bounds(point_a, point_b):
    point_a = np.array(point_a._pos)
    point_b = np.array(point_b._pos)
    # res = np.where(point_a>point_b,point_b,point_a).tolist() + np.where(point_a>point_b,point_a,point_b).tolist()
    return tuple(point_a.tolist() + point_b.tolist())


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_rtree(self):
        swctree = SwcTree()
        swctree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\30_18_10_test.swc")
        rtree = get_edge_rtree(swctree)
        id_edge_dict = get_idedge_dict(swctree)
        point = SwcNode(center=[22.5822, 172.856, 300.413])
        (line_tuple, dis) = get_nearby_edges(rtree, point, id_edge_dict, point.radius())[0]

        print(point.distance(Line(coords=[[15.3249, 130.821, 327.012],[19.8495, 132.384, 323.395]])))
        print("dis = {}, line:{}, {}".format(
            dis, line_tuple[0]._pos,line_tuple[1]._pos
        ))


if __name__ == "__main__":
    unittest.main()