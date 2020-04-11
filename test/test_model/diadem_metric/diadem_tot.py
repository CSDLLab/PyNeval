import unittest
from pymets.metric.diadem_metric import diadem_metric
from pymets.model.swc_node import SwcNode, SwcTree
from pymets.metric.utils.config_utils import get_default_threshold
from pymets.io.read_json import read_json


class DiademTotTest(unittest.TestCase):
    def test_1(self):
        testTree = SwcTree()
        goldTree = SwcTree()
        goldTree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\diadem\diadem3.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\diadem\diadem3.swc")

        # goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\\gold\\ExampleGoldStandard.swc")
        # testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\ExampleTest.swc")
        get_default_threshold(goldTree)

        score = diadem_metric(swc_test_tree=testTree,
                              swc_gold_tree=goldTree,
                              config=read_json("D:\gitProject\mine\PyMets\config\diadem_metric.json"))
        print(score)
        self.assertEqual(score, 1.0)

    def test_2(self):
        testTree = SwcTree()
        goldTree = SwcTree()
        goldTree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\diadem\diadem4.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\diadem\diadem4.swc")

        # goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\\gold\\ExampleGoldStandard.swc")
        # testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\ExampleTest.swc")
        get_default_threshold(goldTree)

        score = diadem_metric(swc_test_tree=testTree,
                              swc_gold_tree=goldTree,
                              config=read_json("D:\gitProject\mine\PyMets\config\diadem_metric.json"))
        print(score)
        self.assertEqual(score, 0.5)

    def test_3(self):
        testTree = SwcTree()
        goldTree = SwcTree()
        goldTree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\ExampleGoldStandard.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\ExampleTest.swc")

        # goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\\gold\\ExampleGoldStandard.swc")
        # testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\\ExampleTest.swc")
        get_default_threshold(goldTree)

        score = diadem_metric(swc_test_tree=testTree,
                              swc_gold_tree=goldTree,
                              config=read_json("D:\gitProject\mine\PyMets\config\diadem_metric.json"))
        print(score)
        self.assertEqual(score, 0.9564541213063764)

    def test_4(self):
        testTree = SwcTree()
        goldTree = SwcTree()
        goldTree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\diadem\diadem8.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\diadem\diadem8.swc")

        get_default_threshold(goldTree)

        score = diadem_metric(swc_test_tree=testTree,
                              swc_gold_tree=goldTree,
                              config=read_json("D:\gitProject\mine\PyMets\config\diadem_metric.json"))
        print(score)
        self.assertEqual(score, 1.0)

    def test_5(self):
        testTree = SwcTree()
        goldTree = SwcTree()
        goldTree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\diadem\diadem7.swc")
        testTree.load("D:\gitProject\mine\PyMets\\test\data_example\\test\diadem\diadem7.swc")

        get_default_threshold(goldTree)

        score = diadem_metric(swc_test_tree=testTree,
                              swc_gold_tree=goldTree,
                              config=read_json("D:\gitProject\mine\PyMets\config\diadem_metric.json"))
        print(score)
        self.assertEqual(score, 0.5)


if __name__ == '__main__':
    unittest.main()
