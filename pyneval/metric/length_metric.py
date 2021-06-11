import sys
import jsonschema

from pyneval.model import swc_node
from pyneval.metric.utils import edge_match_utils
from pyneval.io import read_json
from pyneval.io import read_swc
from pyneval.io import swc_writer


def length_metric_run(gold_swc_tree=None, test_swc_tree=None,
                      rad_threshold=-1.0, len_threshold=0.2, debug=False):
    """
    get matched edge set and calculate recall and precision
    Args:
        gold_swc_tree(SwcTree):
        test_swc_tree(SwcTree):
        rad_threshold(float): threshold of key point radius
        len_threshold(float): threshold of length of the matching edges
        debug(bool): list debug info ot not
    Returns:
        tuple: contain two values to demonstrate metric result
            precision(float): percentage of total length of edges that are matched compared to test tree
            recall(float): percentage of total length of edges that are matched compared to gold tree
    Raises:
        None
    """
    # get matched edge set
    match_edges, test_match_length = edge_match_utils.get_match_edges(gold_swc_tree=gold_swc_tree,
                                                                      test_swc_tree=test_swc_tree,
                                                                      rad_threshold=rad_threshold,
                                                                      len_threshold=len_threshold,
                                                                      debug=debug)
    # calculate the sum of matched length and total length of gold and test tree
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
    # calculate recall and precision
    if gold_total_length != 0:
        recall = round(match_length/gold_total_length, 8)
    else:
        recall = 0

    if test_total_length != 0:
        precision = round(test_match_length/test_total_length, 8)
    else:
        precision = 0

    return min(recall, 1.0), min(precision, 1.0)


# @do_cprofile("./mkm_run.prof")
def length_metric(gold_swc_tree, test_swc_tree, config):
    """Main function of length metric.
    unpack config and run the matching function
    Args:
        gold_swc_tree(SwcTree):
        test_swc_tree(SwcTree):
        config(Dict):
            keys: the name of configs
            items: config values
    Example:
        test_tree = swc_node.SwcTree()
        gold_tree = swc_node.SwcTree()
        gold_tree.load("..\\..\\data\\test_data\\geo_metric_data\\gold_fake_data1.swc")
        test_tree.load("..\\..\\data\\test_data\\geo_metric_data\\test_fake_data1.swc")
        lm_res = length_metric(gold_swc_tree=gold_tree,
                               test_swc_tree=test_tree,
                               config=config)
    Returns:
        tuple: contain two values to demonstrate metric result
            precision(float): percentage of total length of edges that are matched compared to test tree
            recall(float): percentage of total length of edges that are matched compared to gold tree
    Raises:
        None
    """

    # read config
    rad_mode = config["rad_mode"]
    rad_threshold = config["rad_threshold"]
    len_threshold = config["len_threshold"]
    scale = config["scale"]
    debug = config["debug"]

    gold_swc_tree.rescale(scale)
    test_swc_tree.rescale(scale)
    gold_swc_tree.set_node_type_by_topo(root_id=1)
    test_swc_tree.set_node_type_by_topo(root_id=5)

    if rad_mode == 1:
        rad_threshold *= -1
    # check every edge in test, if it is overlap with any edge in gold three
    recall, precision = length_metric_run(gold_swc_tree=gold_swc_tree,
                                          test_swc_tree=test_swc_tree,
                                          rad_threshold=rad_threshold,
                                          len_threshold=len_threshold,
                                          debug=debug)

    if "detail_path" in config:
        swc_writer.swc_save(gold_swc_tree, config["detail_path"][:-4]+"_gold.swc")
        swc_writer.swc_save(test_swc_tree, config["detail_path"][:-4]+"_test.swc")
    if debug:
        print("Recall = {}, Precision = {}".format(recall, precision))

    res = {
        "recall": recall,
        "precision": precision
    }
    return res, gold_swc_tree, test_swc_tree


def web_length_metric(gold_swc, test_swc, mode, rad_threshold, len_threshold):
    """
        length metric interface connect to webmets
        (https://github.com/bennieHan/webmets)
        which is not used nowadays
    Args:
        gold_swc(SwcTree):
        test_swc(SwcTree):
        mode(int) 1 or 2, same as "mode" in config
        rad_threshold(float): threshold of key point radius
        len_threshold(float): threshold of length of the matching edges
    Example:
        # in Flask:
        def geometry():
            gold_swc = request.form.get('gold_txt')
            test_swc = request.form.get('test_txt')
            method = request.form.get('method')
            rad_threshold = request.form.get('rad_threshold')
            len_threshold = request.form.get('len_threshold')
            result = web_length_metric(gold_swc=gold_swc,
                                       test_swc=test_swc,
                                       method=int(method),
                                       rad_threshold=rad_threshold,
                                       len_threshold=len_threshold)
            # result['gold_swc'] = adjust_radius_work(result['gold_swc'], 0.1)
            # result['test_swc'] = adjust_radius_work(result['test_swc'], 0.1)
            return jsonify(result=result)
    Returns:
        tuple: contain five values to demonstrate metric result
            precision(float): percentage of total length of edges that are matched compared to test tree
            recall(float): percentage of total length of edges that are matched compared to gold tree
            gold_swc(Swc Tree):
            test_swc(Swc Tree):
            vertical_swc(Swc Tree): vertical edge between gold and test swc tree.
    Raises:
        None
    """
    gold_tree = swc_node.SwcTree()
    test_tree = swc_node.SwcTree()

    gold_tree.load_list(read_swc.adjust_swcfile(gold_swc))
    test_tree.load_list(read_swc.adjust_swcfile(test_swc))

    config = {
        'method': mode,
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
    goldTree = swc_node.SwcTree()
    testTree = swc_node.SwcTree()
    sys.setrecursionlimit(10000000)
    testTree.load("E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\data\example_selected\\a.swc")
    goldTree.load("E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\output\\random_data\move\\a\\020\move_00.swc")

    config = read_json.read_json("..\\..\\config\\length_metric.json")
    config_schema = read_json.read_json("..\\..\\config\\schemas\\length_metric_schema.json")
    try:
        jsonschema.validate(config, config_schema)
    except Exception as e:
        raise Exception("[Error: ]Error in analyzing config json file")
    config["detail_path"] = "..\\..\\output\\length_output\\length_metric_detail.swc"
    
    lm_res = length_metric(gold_swc_tree=goldTree,
                           test_swc_tree=testTree,
                           config=config)

    print("recall    = {}\n"
          "precision = {}\n".format(lm_res["recall"], lm_res["precision"]))
