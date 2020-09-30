import unittest
import sys
from pyneval.metric.branch_leaf_metric import branch_leaf_metric
from pyneval.model.swc_node import SwcTree, SwcNode
from pyneval.io.read_json import read_json


class BranchDetectTest(unittest.TestCase):
    def test_branch1(self):
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\test\data_example\\test\\branch_detect\\194444_new.swc")
        gold_swc_tree.load("..\\..\\..\\test\data_example\gold\\branch_detect\\194444.swc")
        config = read_json("..\\..\\..\\config\\branch_metric.json")
        sys.setrecursionlimit(1000000)
        config['threshold_dis'] = 5
        branch_result, leaf_result = \
            branch_leaf_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
        self.assertEqual(63, branch_result[0])
        self.assertEqual(70, branch_result[1])
        self.assertEqual(1.6464514909060324, branch_result[2])

    def test_branch2(self):
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\test\data_example\\test\\branch_detect\\194444_new.swc")
        gold_swc_tree.load("..\\..\\..\\test\data_example\gold\\branch_detect\\194444.swc")
        config = read_json("..\\..\\..\\config\\branch_metric.json")
        sys.setrecursionlimit(1000000)
        config['threshold_dis'] = 10
        branch_result, leaf_result = \
            branch_leaf_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)

        self.assertEqual(branch_result[0], 42)
        self.assertEqual(branch_result[1], 49)
        self.assertEqual(branch_result[2], 2.2915797279501797)


if __name__ == '__main__':
    unittest.main()
