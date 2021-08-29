import sys
import jsonschema

from pyneval.model import swc_node
from pyneval.metric.utils import edge_match_utils
from pyneval.io import read_swc
from pyneval.io import swc_writer
from pyneval.metric.utils.metric_manager import get_metric_manager

metric_manager = get_metric_manager()


class LengthMetric(object):
    """
    length metric
    """

    def __init__(self, config):
        # read config
        self.radius_mode = config["radius_mode"]
        self.radius_threshold = config["radius_threshold"]
        self.length_threshold = config["length_threshold"]
        self.scale = config["scale"]
        self.debug = config["debug"]

    def length_metric_run(self, gold_swc_tree=None, test_swc_tree=None,
                          radius_threshold=-1.0, length_threshold=0.2):
        """
        get matched edge set and calculate recall and precision
        Args:
            gold_swc_tree(SwcTree):
            test_swc_tree(SwcTree):
            radius_threshold(float): threshold of key point radius
            length_threshold(float): threshold of length of the matching edges
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
                                                                          radius_threshold=radius_threshold,
                                                                          length_threshold=length_threshold,
                                                                          debug=self.debug)
        # calculate the sum of matched length and total length of gold and test tree
        match_length = 0.0
        for line_tuple in match_edges:
            match_length += line_tuple[0].parent_distance()

        gold_total_length = round(gold_swc_tree.length(), 8)
        test_total_length = round(test_swc_tree.length(), 8)
        match_length = round(match_length, 8)
        test_match_length = round(test_match_length, 8)

        if self.debug:
            print("match_length = {}, test_match_length = {}, gold_total_length = {}, test_total_length = {}"
                  .format(match_length, test_match_length, gold_total_length, test_total_length))
        # calculate recall and precision
        if gold_total_length != 0:
            recall = round(match_length / gold_total_length, 8)
        else:
            recall = 0

        if test_total_length != 0:
            precision = round(test_match_length / test_total_length, 8)
        else:
            precision = 0

        return min(recall, 1.0), min(precision, 1.0)

    def run(self, gold_swc_tree, test_swc_tree):
        """Main function of length metric.
            unpack config and run the matching function
            Args:
                gold_swc_tree(SwcTree):
                test_swc_tree(SwcTree):
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
        gold_swc_tree.rescale(self.scale)
        test_swc_tree.rescale(self.scale)
        gold_swc_tree.set_node_type_by_topo(root_id=1)
        test_swc_tree.set_node_type_by_topo(root_id=5)

        if self.radius_mode == 1:
            self.radius_threshold *= -1
        # check every edge in test, if it is overlap with any edge in gold three
        recall, precision = self.length_metric_run(gold_swc_tree=gold_swc_tree,
                                                   test_swc_tree=test_swc_tree,
                                                   radius_threshold=self.radius_threshold,
                                                   length_threshold=self.length_threshold,
                                                   )
        if self.debug:
            print("Recall = {}, Precision = {}".format(recall, precision))

        res = {
            "recall": recall,
            "precision": precision
        }
        return res, gold_swc_tree, test_swc_tree


# @do_cprofile("./mkm_run.prof")
@metric_manager.register(
    name="length",
    config="length_metric.json",
    desc="length of matched branches and fibers",
    public=True,
    alias=['ML']
)
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

    length_metric = LengthMetric(config)
    return length_metric.run(gold_swc_tree, test_swc_tree)


if __name__ == "__main__":
    goldTree = swc_node.SwcTree()
    testTree = swc_node.SwcTree()
    sys.setrecursionlimit(10000000)
    goldTree.load("../../data/test_data/geo_metric_data/gold_fake_data3.swc")
    testTree.load("../../data/test_data/geo_metric_data/test_fake_data3.swc")

    from pyneval.metric.utils import config_utils

    config = config_utils.get_default_configs("length")
    config_schema = config_utils.get_config_schema("length")
    try:
        jsonschema.validate(config, config_schema)
    except Exception as e:
        raise Exception("[Error: ]Error in analyzing config json file")
    config["detail_path"] = "..\\..\\output\\length_output\\length_metric_detail.swc"

    lm_res, _, _ = length_metric(gold_swc_tree=testTree,
                                 test_swc_tree=goldTree,
                                 config=config)

    print("recall    = {}\n"
          "precision = {}\n"
          "f1        = {}".format(lm_res["recall"], lm_res["precision"], (
                lm_res["recall"] * lm_res["precision"] * 2 / (lm_res["recall"] + lm_res["precision"]))))
