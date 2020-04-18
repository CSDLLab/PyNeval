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

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           abs_dir="D:\gitProject\mine\PyMets",
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           abs_dir="D:\gitProject\mine\PyMets",
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        self.assertEqual(recall1, 0.7030284661586385)
        self.assertEqual(recall2, 0.8685749970409651)
        self.assertEqual(precision1, 0.7174338664651955)
        self.assertEqual(precision2, 0.8511348243456205)

    def test_len_2(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\30_18_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\30_18_10_test.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           abs_dir="D:\gitProject\mine\PyMets",
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           abs_dir="D:\gitProject\mine\PyMets",
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        self.assertEqual(recall1, 0.6818040837428125)
        self.assertEqual(recall2, 0.6971179817818407)
        self.assertEqual(precision1, 0.6327624077188985)
        self.assertEqual(precision2, 0.7511474781551107)

    def test_len_3(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\34_23_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\34_23_10_test.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,                                                    
                                                           test_swc_tree=testTree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyMets",                                       
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))   
                                                                                                                                      
        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,                                                    
                                                           test_swc_tree=goldtree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyMets",                                       
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))

        self.assertEqual(recall1, 0.6092362772577844)
        self.assertEqual(recall2, 0.5585330586568052)
        self.assertEqual(precision1, 0.5318779478680355)
        self.assertEqual(precision2, 0.6397682076225172)

    def test_len_4(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\conner.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\conner.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,                                                    
                                                           test_swc_tree=testTree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyMets",                                       
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))   
                                                                                                                                      
        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,                                                    
                                                           test_swc_tree=goldtree,                                                    
                                                           abs_dir="D:\gitProject\mine\PyMets",                                       
                                                           config=read_json("D:\gitProject\mine\PyMets\config\length_metric.json"))
        self.assertEqual(recall1, 1.0)
        self.assertEqual(recall2, 0.0)
        self.assertEqual(precision1, 0.9385873563259137)
        self.assertEqual(precision2, 0.0)


if __name__ == '__main__':
    unittest.main()
