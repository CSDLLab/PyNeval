import unittest, time
from pyneval.io.read_json import read_json
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.metric.length_metric import length_metric


class LengthMetricTest(unittest.TestCase):
    def test_len_1(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\2_18_gold.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\2_18_test.swc")

        start = time.time()
        lm_res = length_metric(gold_swc_tree=goldtree,
                               test_swc_tree=testTree,
                               config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        lm_res2 = length_metric(gold_swc_tree=testTree,
                                test_swc_tree=goldtree,
                                config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        print("2_18 {}".format(time.time()-start))
        self.assertEqual(lm_res[0], 0.74957484)
        self.assertEqual(lm_res2[0], 0.91178429)
        self.assertEqual(lm_res[1], 0.77636927)
        self.assertEqual(lm_res2[1], 0.84352877)

    def test_len_2(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\30_18_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\30_18_10_test.swc")

        start = time.time()
        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
        print("30_18_10 {}".format(time.time()-start))
        self.assertEqual(recall1, 0.95037505)
        self.assertEqual(recall2, 0.88408952)
        self.assertEqual(precision1, 0.88201204)
        self.assertEqual(precision2, 0.95769503)

    def test_len_3(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\34_23_10_gold.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\34_23_10_test.swc")

        start = time.time()
        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,                                                    
                                                           test_swc_tree=testTree,                                                    
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
                                                                                                                                      
        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,                                                    
                                                           test_swc_tree=goldtree,                                                    
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
        print("34_23_10 {}".format(time.time()-start))
        self.assertEqual(recall1, 0.66041513)
        self.assertEqual(recall2, 0.60889348)
        self.assertEqual(precision1, 0.58476999)
        self.assertEqual(precision2, 0.70757075)

    def test_len_4(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\conner.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\conner.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,                                                    
                                                           test_swc_tree=testTree,                                                    
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))
                                                                                                                                      
        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,                                                    
                                                           test_swc_tree=goldtree,                                                    
                                                           config=read_json("D:\gitProject\mine\PyNeval\config\length_metric.json"))

        self.assertEqual(recall1, 1.0)
        self.assertEqual(recall2, 0.0)
        self.assertEqual(precision1, 1.0)
        self.assertEqual(precision2, 0.0)

    def test_len_5(self):
        goldtree = SwcTree()
        testTree = SwcTree()

        goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\multy_useage\push.swc")
        testTree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\multy_useage\push.swc")

        recall1, precision1, vertical_tree = length_metric(gold_swc_tree=goldtree,
                                                           test_swc_tree=testTree,
                                                           config=read_json(
                                                               "D:\gitProject\mine\PyNeval\config\length_metric.json"))

        recall2, precision2, vertical_tree = length_metric(gold_swc_tree=testTree,
                                                           test_swc_tree=goldtree,
                                                           config=read_json(
                                                               "D:\gitProject\mine\PyNeval\config\length_metric.json"))

        self.assertEqual(recall1, 0.76588382)
        self.assertEqual(recall2, 0.39212906)
        self.assertEqual(precision1, 0.40348057)
        self.assertEqual(precision2, 0.75791792)

    def test_len_6(self):
        test_tree = SwcTree()
        gold_tree = SwcTree()
        test_tree.load("../../../data/test_data/geo_metric_data/test/fake_data1.swc")
        gold_tree.load("../../../data/test_data/geo_metric_data/gold/fake_data1.swc")
        config = read_json("../../../config/length_metric.json")

        recall, precision = length_metric(gold_swc_tree=gold_tree, test_swc_tree=test_tree, config=config)
        print(recall)
        print(precision)


if __name__ == '__main__':
    unittest.main()
