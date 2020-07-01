from pyneval.model.swc_node import SwcTree
MAX_DIS = 0x3fffffff


def mse_metric(gold_swc_tree, test_swc_tree):
    gold_swc_list = gold_swc_tree.get_node_list()
    test_swc_list = test_swc_tree.get_node_list()

    avg_dis_1 = 0
    for gold_node in gold_swc_list:
        if gold_node.is_virtual():
            continue
        dis = MAX_DIS
        for test_node in test_swc_list:
            if test_node.is_virtual():
                continue
            dis = min(dis, gold_node.distance(test_node))
        avg_dis_1 += dis
    avg_dis_1 /= (len(gold_swc_list)-1)
    return avg_dis_1


if __name__=="__main__":
    gold_swc_tree = SwcTree()
    test_swc_tree = SwcTree()

    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\branch.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\branch.swc")
    test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\34_23_10_test.swc")
    gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\34_23_10_gold.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\\2_18_test.swc")
    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\2_18_gold.swc")


    # gold_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\mse_hunter.swc")
    # test_swc_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\\test\mse_hunter.swc")
    print(mse_metric(gold_swc_tree, test_swc_tree))
    print(mse_metric(test_swc_tree, gold_swc_tree))


