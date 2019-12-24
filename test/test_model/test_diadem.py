import unittest
from pymets.model.swc_node import SwcTree
from pymets.model.binary_node import convert_to_binarytree
from pymets.metric.diadem_metric import remove_spurs

class TestStringMethods(unittest.TestCase):

    def test_remove_spurs(self):
        goldtree = SwcTree()
        goldtree.load("D:\gitProject\mine\PyMets\\test\data_example\gold\\ExampleGoldStandard.swc")
        bintree = convert_to_binarytree(goldtree)
        spur_set = remove_spurs(bintree, 1.0)
        for item in spur_set:
            print(item.data.get_id())


if __name__ == "__main__":
    unittest.main()