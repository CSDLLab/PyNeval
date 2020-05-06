import unittest, time
from pyneval.io.read_json import read_json
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.metric.length_metric import length_metric
from test.data_builder.dbuilder import build_random


class PymetsTotCase(unittest.TestCase):
    def test_random_1(self):
        move_percentage = 0.1
        move_num = None
        move_range = 1.0
        move_tendency = (1, 1, 1)

        gold_tree = SwcTree()
        gold_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\multy_useage\push.swc")
        test_tree = build_random(swc_tree=gold_tree,
                                 move_percentage=move_percentage,
                                 move_num=move_num,
                                 move_range=move_range,
                                 tendency=move_tendency)

        length_metric(gold_swc_tree=gold_tree,
                      test_swc_tree=test_tree,
                      abs_dir="",
                      config=read_json("..\..\..\config\length_metric.json"))
