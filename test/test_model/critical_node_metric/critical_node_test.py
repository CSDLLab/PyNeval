import unittest
import sys
from pyneval.metric.critical_node_metric import critical_node_metric
from pyneval.model.swc_node import SwcTree, SwcNode
from pyneval.pyneval_io.json_io import read_json


class BranchDetectTest(unittest.TestCase):
    def test_branch1(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\194444.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\194444.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")
        config['threshold_dis'] = 5
        config['mode'] = 1

        branch_result = critical_node_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
        print(branch_result[3])
        print(branch_result[4])
        print(branch_result[5])
        self.assertEqual(61, branch_result[3])
        self.assertEqual(73, branch_result[4])
        self.assertEqual(1.6772653444540893, branch_result[5])

    def test_branch2(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\194444.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\194444.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")
        config['threshold_dis'] = 10
        branch_result = critical_node_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
        print(branch_result[3])
        print(branch_result[4])
        print(branch_result[5])
        self.assertEqual(branch_result[3], 40)
        self.assertEqual(branch_result[4], 52)
        self.assertEqual(branch_result[5], 2.335216925858577)

    def test_branch3(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\fake_data2.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\fake_data2.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")
        config['threshold_dis'] = 10
        branch_result = critical_node_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)

        self.assertEqual(branch_result[3], 0)
        self.assertEqual(branch_result[4], 0)
        self.assertEqual(branch_result[5], 5.031162291335031)

    def test_branch4(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\fake_data3.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\fake_data3.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")
        config['threshold_dis'] = 20
        branch_result = critical_node_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
        self.assertEqual(branch_result[3], 0)
        self.assertEqual(branch_result[4], 0)
        self.assertEqual(branch_result[5], 10.44030650891055)

    def test_branch5(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\fake_data5.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\fake_data5.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")
        config['threshold_dis'] = 10
        branch_result = critical_node_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)

        self.assertEqual(branch_result[3], 0)
        self.assertEqual(branch_result[4], 0)
        self.assertEqual(branch_result[5], 6.073843441985439)

    def test_branch6(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\194444_isolated_node.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\194444.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")
        config['threshold_dis'] = 10
        branch_result = critical_node_metric(test_swc_tree=gold_swc_tree, gold_swc_tree=test_swc_tree, config=config)
        print(branch_result[3])
        print(branch_result[4])
        print(branch_result[5])
        self.assertEqual(branch_result[3], 0)
        self.assertEqual(branch_result[4], 231)
        self.assertEqual(branch_result[5], 0.6151700217681823)

    def test_branch7(self):
        sys.setrecursionlimit(1000000)
        gold_swc_tree = SwcTree()
        test_swc_tree = SwcTree()
        test_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\test\\fake_data1.swc")
        gold_swc_tree.load("..\\..\\..\\data\\test_data\\branch_metric_data\\gold\\fake_data1.swc")
        config = read_json("..\\..\\..\\config\\critical_node_metric.json")

        branch_result = critical_node_metric(test_swc_tree=test_swc_tree,
                                             gold_swc_tree=gold_swc_tree,
                                             config=config)
        ans = [0, 1, 1, 0.0]
        for i in range(2, 6):
            print(branch_result[i])
            self.assertEqual(branch_result[i], ans[i-2])


if __name__ == '__main__':
    unittest.main()
