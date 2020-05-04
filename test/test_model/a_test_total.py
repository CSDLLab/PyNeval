import unittest, time
from pyneval.io.read_json import read_json
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.metric.length_metric import length_metric


class PymetsTotCase(unittest.TestCase):
    def test_len_1(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\2_18_gold.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\2_18_test.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        self.assertEqual(recall1, 0.7030284661586385)
        self.assertEqual(recall2, 0.8685749970409651)
        self.assertEqual(precision1, 0.7174338664651955)
        self.assertEqual(precision2, 0.8511348243456205)

    def test_len_2(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\30_18_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\30_18_10_test.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        self.assertEqual(recall1, 0.950375054330871)
        self.assertEqual(recall2, 0.8810142908724438)
        self.assertEqual(precision1, 0.8820152620869665)
        self.assertEqual(precision2, 0.9492965037509923)

    def test_len_3(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\34_23_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\34_23_10_test.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,                                                    
                                                           test_swc_tree=testTree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
                                                                                                                                      
        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,                                                    
                                                           test_swc_tree=goldtree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        self.assertEqual(recall1, 0.6106312743663942)
        self.assertEqual(recall2, 0.5605183853340827)
        self.assertEqual(precision1, 0.533095813952355)
        self.assertEqual(precision2, 0.6420422876795178)

    def test_len_4(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\conner.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\conner.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,                                                    
                                                           test_swc_tree=testTree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
                                                                                                                                      
        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,                                                    
                                                           test_swc_tree=goldtree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
        self.assertEqual(recall1, 1.0)
        self.assertEqual(recall2, 0.0)
        self.assertEqual(precision1, 0.9385873563259137)
        self.assertEqual(precision2, 0.0)

    def test_len_5(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\multy_useage\push.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\multy_useage\push.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json(
                                                               "D:\gitProject\mine\PyNeval\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           abs_dir="D:\gitProject\mine\PyNeval",
                                                           config=read_json(
                                                               "D:\gitProject\mine\PyNeval\config\length_metric.json"))

        self.assertEqual(recall1, 0.7658838154509461)
        self.assertEqual(recall2, 0.39212905869489334)
        self.assertEqual(precision1, 0.3969882713291548)
        self.assertEqual(precision2, 0.7565092505552242)


if __name__ == '__main__':
    unittest.main()
