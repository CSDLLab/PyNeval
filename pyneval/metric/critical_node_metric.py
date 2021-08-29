import sys
import jsonschema

from pyneval.model import swc_node
from pyneval.metric.utils import km_utils
from pyneval.metric.utils import point_match_utils
from pyneval.metric.utils.metric_manager import get_metric_manager
from pyneval.metric.utils import bigraph_maxmatch_utils
metric_manager = get_metric_manager()


class CriticalNodeMetric(object):
    """
    critical node metric
    """
    def __init__(self, config):
        # read configs
        self.debug = config["debug"] if config.get("debug") is not None else False
        self.distance_threshold = config["distance_threshold"]
        self.critical_type = config["critical_type"]
        self.scale = config["scale"]
        self.true_positive = config["true_positive"]
        self.missed = config["missed"]
        self.excess = config["excess"]

    def get_result(self, test_len, gold_len, switch, km, threshold_dis):
        false_pos_num, false_neg_num, true_pos_num = 0, 0, 0
        # count number of nodes which are matched, calculate FP, TN, TP
        for i in range(gold_len):
            if km.match[i] != -1 and km.G[km.match[i]][i] != -0x3F3F3F3F / 2:
                true_pos_num += 1
        false_neg_num = gold_len - true_pos_num
        false_pos_num = test_len - true_pos_num

        # definition of swich is in function "get_dis_graph"
        if switch:
            false_neg_num, false_pos_num = false_pos_num, false_neg_num
            gold_len, test_len = test_len, gold_len

        if true_pos_num != 0:
            mean_dis = -km.get_max_dis() / true_pos_num
        else:
            mean_dis = 0.0
        if mean_dis == -0.0:
            mean_dis = 0.0

        pt_cost = -km.get_max_dis() + threshold_dis * (false_neg_num + false_pos_num) / (
            false_neg_num + false_pos_num + true_pos_num
        )

        # debug:
        # print("output")
        # print(false_pos_num)
        # print(true_neg_num)
        # print(mean_dis)
        # print(pt_cost)
        return gold_len, test_len, true_pos_num, false_neg_num, false_pos_num, mean_dis, mean_dis * true_pos_num, pt_cost

    def get_colored_tree(self, gold_node_list, test_node_list, MaxMatch, color):
        """
        color[0] = tp's color
        color[1] = fp's color
        color[2] = fn's color
        """
        for i in range(len(gold_node_list)):
            if MaxMatch.pa[i] != -1:
                gold_node_list[i]._type = color[0]
            else:
                gold_node_list[i]._type = color[2]
        for i in range(len(test_node_list)):
            if MaxMatch.pb[i] != -1:
                test_node_list[i]._type = color[0]
            else:
                test_node_list[i]._type = color[1]

    def KM_max_match(
            self,
        gold_tree,
        test_tree,
        test_node_list,
        gold_node_list,
        threshold_dis,
    ):
        """
        get minimum matching distance by running KM algorithm
        than calculate the return value according to matching result
        Args:
            gold_tree(Swc Tree)
            test_tree(Swc Tree)
            gold_node_list(List): contains only branch nodes
            test_node_list(List): contains only branch nodes
            threshold_dis: if the distance of two node are larger than this threshold,
                           they are considered unlimited far
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
        test_gold_dict = point_match_utils.get_swc2swc_dicts(
            src_node_list=test_tree.get_node_list(), tar_node_list=gold_tree.get_node_list()
        )
        # disgraph is a 2D ndarray store the distance between nodes in gold and test
        # test_node_list contains only branch or leaf nodes
        dis_graph, switch, test_len, gold_len = km_utils.get_dis_graph(
            gold_tree=gold_tree,
            test_tree=test_tree,
            test_node_list=test_node_list,
            gold_node_list=gold_node_list,
            test_gold_dict=test_gold_dict,
            threshold_dis=threshold_dis,
            metric_mode=1,
        )
        # create a KM object and calculate the minimum match
        km = km_utils.KM(maxn=max(test_len, gold_len) + 10, nx=test_len, ny=gold_len, G=dis_graph)
        km.solve()
        # calculate the result
        gold_len, test_len, true_pos_num, false_neg_num, false_pos_num, mean_dis, tot_dis, pt_cost = self.get_result(
            test_len=test_len, gold_len=gold_len, switch=switch, km=km, threshold_dis=threshold_dis
        )
        # calculate the number of isolated nodes
        iso_node_num = 0
        for node in test_tree.get_node_list():
            if node.is_isolated():
                iso_node_num += 1
        return gold_len, test_len, true_pos_num, false_neg_num, false_pos_num, mean_dis, tot_dis, pt_cost, iso_node_num

    def max_match(self, test_node_list, gold_node_list, distance_threshold):
        gold_list_len = len(gold_node_list)
        test_list_len = len(test_node_list)
        MaxMatch = bigraph_maxmatch_utils.AugmentPath(gold_list_len, test_list_len)
        for i in range(len(gold_node_list)):
            for j in range(len(test_node_list)):
                dis = gold_node_list[i].distance(test_node_list[j])
                if dis <= distance_threshold:
                    MaxMatch.add(i, j)
        MaxMatch.solve()
        return MaxMatch

    def get_total_dis(self, gold_critical_swc_list, test_critical_swc_list, MaxMatch):
        dis = 0
        for i in range(len(MaxMatch.pa)):
            if MaxMatch.pa[i] == -1:
                continue
            dis += gold_critical_swc_list[i].distance(test_critical_swc_list[MaxMatch.pa[i]])
        return dis

    def run(self, gold_swc_tree, test_swc_tree):
        # rescale the input tree
        gold_swc_tree.rescale(self.scale)
        test_swc_tree.rescale(self.scale)

        # denote the color id of different type of nodes.
        color = [self.true_positive, self.missed, self.excess]
        gold_swc_tree.type_clear(0, 0)
        test_swc_tree.type_clear(0, 0)

        test_critical_swc_list = []
        gold_critical_swc_list = []
        # critical_type == 1: both branches and leaves
        # critical_type == 2: only leaves
        # critical_type == 3: only branches
        if self.critical_type != 2:
            test_critical_swc_list.extend(test_swc_tree.get_branch_swc_list())
            gold_critical_swc_list.extend(gold_swc_tree.get_branch_swc_list())
        if self.critical_type != 3:
            test_critical_swc_list.extend(test_swc_tree.get_leaf_swc_list())
            gold_critical_swc_list.extend(gold_swc_tree.get_leaf_swc_list())

        MaxMatch = self.max_match(
            test_node_list=test_critical_swc_list,
            gold_node_list=gold_critical_swc_list,
            distance_threshold=self.distance_threshold
        )
        # get a colored tree with
        self.get_colored_tree(
            gold_node_list=gold_critical_swc_list, test_node_list=test_critical_swc_list,
            MaxMatch=MaxMatch, color=color
        )

        precision = MaxMatch.res / len(test_critical_swc_list)
        recall = MaxMatch.res / len(gold_critical_swc_list)
        tot_dis = self.get_total_dis(gold_critical_swc_list, test_critical_swc_list, MaxMatch)
        branch_result = {
            "gold_len": len(gold_critical_swc_list),
            "test_len": len(test_critical_swc_list),
            "true_pos_num": MaxMatch.res,
            "false_neg_num": len(gold_critical_swc_list) - MaxMatch.res,
            "false_pos_num": len(test_critical_swc_list) - MaxMatch.res,
            "precision": precision,
            "recall": recall,
            "mean_dis": tot_dis/MaxMatch.res,
            "tot_dis": tot_dis,
            "f1_score": 2*precision*recall/(precision + recall),
        }
        return branch_result, gold_swc_tree, test_swc_tree

@metric_manager.register(
    name="cn",
    config="critical_node_metric.json",
    desc="quality of critical points",
    public=True,
    alias=["CN"],
)
def critical_node_metric(gold_swc_tree, test_swc_tree, config):
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

    critical_node = CriticalNodeMetric(config)
    return critical_node.run(gold_swc_tree, test_swc_tree)


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    file_name = "fake_data11"
    gold_swc_tree = swc_node.SwcTree()
    test_swc_tree = swc_node.SwcTree()

    gold_swc_tree.load("../../data\\test_data\geo_metric_data\gold_34_23_10.swc")
    test_swc_tree.load("../../data\\test_data\geo_metric_data\\test_34_23_10.swc")
    from pyneval.metric.utils import config_utils

    config = config_utils.get_default_configs("cn")
    config["critical_type"] = 2
    config_schema = config_utils.get_config_schema("cn")
    try:
        jsonschema.validate(config, config_schema)
    except Exception as e:
        raise Exception("[Error: ]Error in analyzing config json file")

    branch_result, _, _ = critical_node_metric(test_swc_tree=test_swc_tree, gold_swc_tree=gold_swc_tree, config=config)
    print ("---------------Result---------------")
    print (
        "gole_branch_num = {}, test_branch_num = {}\n"
        "true_positive_number  = {}\n"
        "false_negative_num    = {}\n"
        "false_positive_num    = {}\n"
        "precision             = {}\n"
        "recall                = {}\n"
        "matched_mean_distance = {}\n"
        "matched_sum_distance  = {}\n"
        "f1_score              = {}".format(
            branch_result["gold_len"],
            branch_result["test_len"],
            branch_result["true_pos_num"],
            branch_result["false_neg_num"],
            branch_result["false_pos_num"],
            branch_result["precision"],
            branch_result["recall"],
            branch_result["mean_dis"],
            branch_result["tot_dis"],
            branch_result["f1_score"],
        )
    )
    print ("----------------End-----------------")
