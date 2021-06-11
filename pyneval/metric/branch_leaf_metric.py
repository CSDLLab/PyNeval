import sys
import jsonschema

from pyneval.io import read_json
from pyneval.model import swc_node
from pyneval.metric.utils import km_utils
from pyneval.metric.utils import point_match_utils


def get_result(test_len, gold_len, switch, km, threshold_dis):
    false_pos_num, false_neg_num, true_pos_num = 0, 0, 0
    # count numer of nodes which are matched, calculate FP, TN, TP
    for i in range(0, gold_len):
        if km.match[i] != -1 and km.G[km.match[i]][i] != -0x3f3f3f3f / 2:
            true_pos_num += 1
    false_neg_num = gold_len - true_pos_num
    false_pos_num = test_len - true_pos_num

    # definition of swich is in function "get_dis_graph"
    if switch:
        false_neg_num, false_pos_num = false_pos_num, false_neg_num

    if true_pos_num != 0:
        mean_dis = -km.get_max_dis() / true_pos_num
    else:
        mean_dis = 0.0
    if mean_dis == -0.0:
        mean_dis = 0.0

    pt_cost = -km.get_max_dis() + threshold_dis * (false_neg_num + false_pos_num) / (
                false_neg_num + false_pos_num + true_pos_num)

    # debug:
    # print("output")
    # print(false_pos_num)
    # print(true_neg_num)
    # print(mean_dis)
    # print(pt_cost)
    return true_pos_num, false_neg_num, false_pos_num, mean_dis, mean_dis * true_pos_num, pt_cost


def get_colored_tree(test_node_list, gold_node_list, switch, km, color):
    '''
    color[0] = tp's color
    color[1] = fp's color
    color[2] = fn's color
    '''
    tp_set = set()
    for i in range(0, len(gold_node_list)):
        if km.match[i] != -1 and km.G[km.match[i]][i] != -0x3f3f3f3f / 2:
            gold_node_list[i]._type = color[0]
            test_node_list[km.match[i]]._type = color[0]
            tp_set.add(test_node_list[km.match[i]])
        else:
            if switch:
                gold_node_list[i]._type = color[1]
            else:
                gold_node_list[i]._type = color[2]
    for node in test_node_list:
        if node not in tp_set:
            if switch:
                node._type = color[2]
            else:
                node._type = color[1]


def score_point_distance(gold_tree: swc_node.SwcTree, test_tree: swc_node.SwcTree,
                         test_node_list: list, gold_node_list: list,
                         threshold_dis: float, color: list):
    """
    get minimum matching distance by running KM algorithm
    than calculte the return value according to matching result
    Args:
        gold_tree(Swc Tree)
        test_tree(Swc Tree)
        gold_node_list(List): contains only branch nodes
        test_node_list(List): contains only branch nodes
        threshold_dis: if the distance of two node are larger than this threshold,
                       they are considered unlimited far
        color(List): color id of tp, fn, fp nodes
    Returns:
        gold_len(int): length of gold_node_list
        test_len(int): length of test_node_list
        true_pos_num(int): number of nodes in both gold and test tree
        false_neg_num(int): number of nodes in gold but not test tree
        false_pos_num(int): number of nodes in test but not gold tree
        mean_dis: mean distance of nodes that are successfully matched(true positive)
        tot_dis: total distance of nodes that are successfully matched(true positive)
        pt_cost: a composite value calculated by tp, fn, fp and threshold
        iso_node_num: number of nodes in test tree without parents or children
    """
    test_gold_dict = point_match_utils.get_swc2swc_dicts(src_node_list=test_tree.get_node_list(),
                                                         tar_node_list=gold_tree.get_node_list())
    # disgraph is a 2D ndarray store the distance between nodes in gold and test
    # test_node_list contains only branch or leaf nodes
    dis_graph, switch, test_len, gold_len = km_utils.get_dis_graph(gold_tree=gold_tree,
                                                                   test_tree=test_tree,
                                                                   test_node_list=test_node_list,
                                                                   gold_node_list=gold_node_list,
                                                                   test_gold_dict=test_gold_dict,
                                                                   threshold_dis=threshold_dis,
                                                                   metric_mode=1)
    # create a KM object and calculate the minimum match
    km = km_utils.KM(maxn=max(test_len, gold_len)+10, nx=test_len, ny=gold_len, G=dis_graph)
    km.solve()
    # calculate the result
    true_pos_num, false_neg_num, false_pos_num, \
    mean_dis, tot_dis, pt_cost = get_result(test_len=test_len,
                                            gold_len=gold_len,
                                            switch=switch,
                                            km=km,
                                            threshold_dis=threshold_dis)
    # calculate the number of isolated nodes
    iso_node_num = 0
    for node in test_tree.get_node_list():
        if node.is_isolated():
            iso_node_num += 1
    # get a colored tree with
    get_colored_tree(test_node_list=test_node_list, gold_node_list=gold_node_list,
                     switch=switch, km=km, color=color)
    return gold_len, test_len, true_pos_num, false_neg_num, false_pos_num, \
           mean_dis, tot_dis, pt_cost, iso_node_num


def branch_leaf_metric(gold_swc_tree, test_swc_tree, config):
    """
    branch metric calculates the minimum distance match between branches of two swc trees
    This function is used for unpacking configs and packaging return values
    Args:
        gold_swc_tree(Swc Tree) gold standard tree
        test_swc_tree(Swc Tree) reconstructed tree
        config(dict):
            keys: the name of configs
            items: config values
    Example:
        test_tree = swc_node.SwcTree()
        gold_tree = swc_node.SwcTree()
        gold_tree.load("..\\..\\data\\test_data\\topo_metric_data\\gold_fake_data1.swc")
        test_tree.load("..\\..\\data\\test_data\\topo_metric_data\\test_fake_data1.swc")
        branch_result = length_metric(gold_swc_tree=gold_tree,
                                      test_swc_tree=test_tree,
                                      config=config)
        print(branch_result["mean_dis"])
        ...
    Return:
         branch_result(tuple) a tuple of 9 metric results
    """
    # read configs
    threshold_dis = config["threshold_dis"]
    threshold_mode = config["threshold_mode"]
    scale = config["scale"]

    gold_swc_tree.rescale(scale)
    test_swc_tree.rescale(scale)
    # in threshold mode 2, threshold is a multiple of the average length of edges
    if threshold_mode == 2:
        # length of the entire gold swc forest
        tot_dis = gold_swc_tree.length()
        # number of edges in the forest
        edge_num = len(gold_swc_tree.get_node_list())-1-len(gold_swc_tree.root().children)
        threshold_dis = threshold_dis * tot_dis / edge_num
    # denote the color id of different type of nodes.
    color = [
        config["true_positive"],
        config["missed"],
        config["excess"]
    ]
    gold_swc_tree.type_clear(0, 0)
    test_swc_tree.type_clear(0, 0)
    test_branch_swc_list = test_swc_tree.get_branch_swc_list()
    gold_branch_swc_list = gold_swc_tree.get_branch_swc_list()

    branch_result_tuple = score_point_distance(gold_tree=gold_swc_tree,
                                               test_tree=test_swc_tree,
                                               test_node_list=test_branch_swc_list,
                                               gold_node_list=gold_branch_swc_list,
                                               threshold_dis=threshold_dis,
                                               color=color)

    branch_result = {
        "gold_len": branch_result_tuple[0],
        "test_len": branch_result_tuple[1],
        "true_pos_num": branch_result_tuple[2],
        "false_neg_num": branch_result_tuple[3],
        "false_pos_num": branch_result_tuple[4],
        "mean_dis": branch_result_tuple[5],
        "tot_dis": branch_result_tuple[6],
        "pt_cost": branch_result_tuple[7],
        "iso_node_num": branch_result_tuple[8]
    }
    return branch_result, gold_swc_tree, test_swc_tree


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    file_name = "fake_data11"
    gold_swc_tree = swc_node.SwcTree()
    test_swc_tree = swc_node.SwcTree()

    gold_swc_tree.load("../../data/example_selected/a.swc")
    test_swc_tree.load("../../output/random_data/move/a/010/move_03.swc")

    config = read_json.read_json("..\\..\\config\\branch_metric.json")
    config_schema = read_json.read_json("..\\..\\config\\schemas\\branch_metric_schema.json")
    try:
        jsonschema.validate(config, config_schema)
    except Exception as e:
        raise Exception("[Error: ]Error in analyzing config json file")

    branch_result = \
        branch_leaf_metric(test_swc_tree=test_swc_tree, gold_swc_tree=gold_swc_tree, config=config)
    print("---------------Result---------------")
    print("gole_branch_num = {}, test_branch_num = {}\n"
          "true_positive_number  = {}\n"
          "false_negative_num    = {}\n"
          "false_positive_num    = {}\n"
          "matched_mean_distance = {}\n"
          "matched_sum_distance  = {}\n"
          "pt_score              = {}\n"
          "isolated node number  = {}".
          format(branch_result["gold_len"], branch_result["test_len"], branch_result["true_pos_num"],
                 branch_result["false_neg_num"], branch_result["false_pos_num"], branch_result["mean_dis"],
                 branch_result["tot_dis"], branch_result["pt_cost"], branch_result["iso_node_num"]))
    print("----------------End-----------------")
    # with open("../../output/branch_metric/{}_gold.swc".format(file_name), 'w') as f:
    #     f.write(gold_swc_tree.to_str_list())
    # with open("../../output/branch_metric/{}_test.swc".format(file_name), 'w') as f:
    #     f.write(test_swc_tree.to_str_list())

