import sys
import jsonschema

from pyneval.model.swc_node import SwcTree
from pyneval.metric.utils.edge_match_utils import get_match_edges
from pyneval.io.read_json import read_json
from pyneval.io.read_swc import adjust_swcfile
from pyneval.io.read_config import read_float_config, read_path_config, read_bool_config
from pyneval.io.swc_writer import swc_save


def length_metric_run(gold_swc_tree=None, test_swc_tree=None,
                      rad_threshold=-1.0, len_threshold=0.2, debug=False):
    """
    Description: Detail of length metric, get best edge for each edge and calculate final scores
    Input: gold/test swc tree, and parsed configs
    Output: recall(int), precision(int) and vertical Auxiliary line between swc trees
    """
    vertical_tree = []

    match_edges, test_match_length = get_match_edges(gold_swc_tree=gold_swc_tree,
                                                     test_swc_tree=test_swc_tree,  # tree data
                                                     vertical_tree=vertical_tree,  # a empty Auxiliary line tree
                                                     rad_threshold=rad_threshold,
                                                     len_threshold=len_threshold,
                                                     debug=debug)  # configs

    match_length = 0.0
    for line_tuple in match_edges:
        match_length += line_tuple[0].parent_distance()

    gold_total_length = round(gold_swc_tree.length(), 8)
    test_total_length = round(test_swc_tree.length(), 8)
    match_length = round(match_length, 8)
    test_match_length = round(test_match_length, 8)

    if debug:
        print("match_length = {}, test_match_length = {}, gold_total_length = {}, test_total_length = {}"
              .format(match_length, test_match_length, gold_total_length, test_total_length))

    if gold_total_length != 0:
        recall = round(match_length/gold_total_length, 8)
    else:
        recall = 0

    if test_total_length != 0:
        precision = round(test_match_length/test_total_length, 8)
    else:
        precision = 0

    return min(recall, 1.0), min(precision, 1.0), vertical_tree


# @do_cprofile("./mkm_run.prof")
def length_metric(gold_swc_tree, test_swc_tree, config):
    """
    Description: Main function of length metric, parse configs and preprocess data
    Input: gold/test swc tree, config
    Output: recall(int) and precision(int)
    """
    # read config
    rad_mode = config["rad_mode"]
    rad_threshold = config["rad_threshold"]
    len_threshold = config["len_threshold"]
    debug = config["debug"]

    if rad_mode == 1:
        rad_threshold *= -1
    # check every edge in test, if it is overlap with any edge in gold three
    recall, precision, vertical_tree = length_metric_run(gold_swc_tree=gold_swc_tree,
                                                         test_swc_tree=test_swc_tree,
                                                         rad_threshold=rad_threshold,
                                                         len_threshold=len_threshold,
                                                         debug=debug)

    if "detail_path" in config:
        swc_save(gold_swc_tree, config["detail_path"][:-4]+"_gold.swc")
        swc_save(test_swc_tree, config["detail_path"][:-4]+"_test.swc")
    if debug:
        print("Recall = {}, Precision = {}".format(recall, precision))

    res = {
        "recall": recall,
        "precision": precision
    }
    return res


# length metric interface connect to webmets
def pyneval_length_metric(gold_swc, test_swc, method, rad_threshold, len_threshold):
    gold_tree = SwcTree()
    test_tree = SwcTree()

    gold_tree.load_list(adjust_swcfile(gold_swc))
    test_tree.load_list(adjust_swcfile(test_swc))

    config = {
        'method': method,
        'len_threshold': len_threshold,
        'rad_threshold': rad_threshold
    }

    lm_res = length_metric(gold_swc_tree=gold_tree,
                           test_swc_tree=test_tree,
                           config=config)

    result = {
        'recall': lm_res[0],
        'precision': lm_res[1],
        'gold_swc': gold_tree.to_str_list(),
        'test_swc': test_tree.to_str_list(),
        'vertical_swc': lm_res[2]
    }
    return result


if __name__ == "__main__":
    goldTree = SwcTree()
    testTree = SwcTree()
    sys.setrecursionlimit(10000000)
    goldTree.load("..\\..\\data\\test_data\\geo_metric_data\\gold_34_23_10.swc")
    testTree.load("..\\..\\data\\test_data\\geo_metric_data\\test_34_23_10.swc")

    config = read_json("..\\..\\config\\volume_metric.json")
    config_schema = read_json("..\\..\\config\\schemas\\volume_metric_schema.json")

    try:
        jsonschema.validate(config, config_schema)
    except Exception as e:
        raise Exception("[Error: ]Error in analyzing config json file")
    config["detail_path"] = "..\\..\\output\\length_output\\length_metric_detail.swc"

    lm_res = length_metric(gold_swc_tree=goldTree,
                           test_swc_tree=testTree,
                           config=config)

    print("recall    = {}\n"
          "precision = {}\n".format(lm_res[0], lm_res[1]))