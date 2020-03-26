import unittest, time
from pymets.io.read_json import read_json
from pymets.model.swc_node import SwcNode, SwcTree
from pymets.metric.length_metric import length_metric


class PymetsTotCase(unittest.TestCase):
    def test_len_1(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\2_18_gold.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\2_18_test.swc")

        recall1, precision1 = length_metric(gold_swc_tree=goldtree,
                              test_swc_tree=testTree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        recall2, precision2 = length_metric(gold_swc_tree=testTree,
                              test_swc_tree=goldtree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
        self.assertEqual(recall1, 0.7175182998089098)
        self.assertEqual(recall2, 0.8930890142399355)
        self.assertEqual(precision1, 0.7322206039595575)
        self.assertEqual(precision2, 0.8751566230316667)

    def test_len_2(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\30_18_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\30_18_10_test.swc")

        recall1, precision1 = length_metric(gold_swc_tree=goldtree,
                              test_swc_tree=testTree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        recall2, precision2 = length_metric(gold_swc_tree=testTree,
                              test_swc_tree=goldtree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
        self.assertEqual(recall1, 0.950375054330871)
        self.assertEqual(recall2, 0.8810142908724438)
        self.assertEqual(precision1, 0.8820152620869665)
        self.assertEqual(precision2, 0.9492965037509923)

    def test_len_3(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\34_23_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\34_23_10_test.swc")

        recall1, precision1 = length_metric(gold_swc_tree=goldtree,
                              test_swc_tree=testTree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        recall2, precision2 = length_metric(gold_swc_tree=testTree,
                              test_swc_tree=goldtree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
        self.assertEqual(recall1, 0.6166649355625093)
        self.assertEqual(recall2, 0.5681883662381514)
        self.assertEqual(precision1, 0.5383633455405351)
        self.assertEqual(precision2, 0.6508278194568053)

    def test_len_4(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\conner.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\conner.swc")

        recall1, precision1 = length_metric(gold_swc_tree=goldtree,
                              test_swc_tree=testTree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        recall2, precision2 = length_metric(gold_swc_tree=testTree,
                              test_swc_tree=goldtree,
                              abs_dir="D:\gitProject\mine\PyMets",
                              config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
        self.assertEqual(recall1, 1.0)
        self.assertEqual(recall2, 0.0)
        self.assertEqual(precision1, 0.9385873563259137)
        self.assertEqual(precision2, 0.0)

if __name__ == '__main__':
    unittest.main()
