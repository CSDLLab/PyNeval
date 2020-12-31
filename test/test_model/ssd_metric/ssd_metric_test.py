import unittest
import sys
from pyneval.metric.ssd_metric import ssd_metric
from pyneval.model.swc_node import SwcTree, SwcNode
from pyneval.io.read_json import read_json


class SSDMetricTest(unittest.TestCase):
    def test_ssd_1(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\ssd_data\\test\\fake_data1.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\ssd_data\\gold\\fake_data1.swc")
        config = read_json("..\\..\\..\\config\\ssd_metric.json")
        config['threshold_dis'] = 10
        ssd_result = ssd_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
        ans = [1.0920186279062936, 0.92, 0.8666666666666667]
        for i in range(3):
            print(ssd_result[i])
            self.assertEqual(ssd_result[i], ans[i])


if __name__ == '__main__':
    unittest.main()