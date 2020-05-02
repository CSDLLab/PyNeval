import unittest
from pyneval.model.swc_node import SwcTree
from pyneval.metric.diadem_metric import remove_spurs, generate_node_weights, g_weight_dict
from pyneval.metric.utils.bin_utils import convert_to_binarytree


def test_get_bintree():
    goldtree = SwcTree()
    goldtree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\ExampleTest.swc")
    bintree = convert_to_binarytree(goldtree)
    return bintree


class TestStringMethods(unittest.TestCase):

    def test_remove_spurs(self):
        bintree = test_get_bintree()
        spur_set = remove_spurs(bintree, 1.0)
        for item in spur_set:
            print(item.data.get_id())

    def test_weight(self):
        bin_tree = test_get_bintree()
        generate_node_weights(bin_tree, set())
        for key in g_weight_dict.keys():
            print("key = {}, num = {}".format(
                key.data._id, g_weight_dict[key]
            ))

    def testTra(self):
        bin_tree = test_get_bintree()
        bin_tree_list = bin_tree.get_node_list()
        for node in bin_tree_list:
            print(node.data.get_id())
            if node.data.parent_trajectory is not None:
                print(node.data.parent_trajectory._pos)
            if node.data.left_trajectory is not None:
                print(node.data.left_trajectory._pos)
            if node.data.right_trajectory is not None:
                print(node.data.right_trajectory._pos)
            print("------------------------")

if __name__ == "__main__":
    unittest.main()