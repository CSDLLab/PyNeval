from zss import simple_distance, Node
from pyneval.model.swc_node import SwcNode, SwcTree


def swc_to_zss(swc_node):
    cur_node = Node("a")
    for son in swc_node.children:
        son_zss = swc_to_zss(son)
        cur_node.addkid(son_zss)
    return cur_node


if __name__=="__main__":
    gold_swc_tree = SwcTree()
    test_swc_tree = SwcTree()

    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\branch.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\branch.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\ExampleGoldStandard.swc")
    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\ExampleTest.swc")
    gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\diadem\dia_ted1.swc")
    test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\diadem\dia_ted1.swc")
    test_zss_tree = swc_to_zss(test_swc_tree.root())
    gold_zss_tree = swc_to_zss(gold_swc_tree.root())
    print(simple_distance(gold_zss_tree, test_zss_tree))
