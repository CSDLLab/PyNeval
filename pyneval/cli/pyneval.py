import argparse
import sys
import os
import platform
from pyneval.io.read_swc import read_swc_trees
from pyneval.io.read_json import read_json
from pyneval.io.save_swc import swc_save
from pyneval.io.read_tiff import read_tiffs
from pyneval.metric.diadem_metric import diadem_metric
from pyneval.metric.length_metric import length_metric
from pyneval.metric.volume_metric import volume_metric
from pyneval.metric.branch_leaf_metric import branch_leaf_metric
from pyneval.metric.link_metric import link_metric

metric_list = [
    "diadem_metric",
    "overall_length",
    "matched_length",
    "volume_metric",
    "branch_metric",
    "link_metric",
    "DM", "OL", "ML", "VM", "BM", "LM"
]


def read_parameters():
    parser = argparse.ArgumentParser(
        description="pyneval 1.0"
    )

    parser.add_argument(
        "--test",
        "-T",
        help="the route of the test file",
        required=False,
        nargs='*',
    )
    parser.add_argument(
        "--gold",
        "-G",
        help="the route of the gold file",
        required=True
    )
    parser.add_argument(
        "--metric",
        "-M",
        help="choose a metric method",
        required=True
    )
    parser.add_argument(
        "--output",
        "-O",
        help="the route of the output file.\nif not specified, output to screen",
        required=False
    )
    parser.add_argument(
        "--config",
        "-C",
        help="special config for different metric method",
        required=False
    )
    parser.add_argument(
        "--reverse",
        "-R",
        help="output the answer when we switch the gold and test tree",
        required=False
    )
    parser.add_argument(
        "--debug",
        "-D",
        help="Print debug info or not",
        required=False
    )
    return parser.parse_args()


# command program
def run(DEBUG=True):
    # init path parameter
    abs_dir = os.path.abspath("")
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir, "src"))
    sys.path.append(os.path.join(abs_dir, "test"))
    sys.setrecursionlimit(1000000)

    # read parameter
    args = read_parameters()

    # set config
    # gold/test files
    if args.test is None:
        test_swc_files = []
    else:
        test_swc_files = [os.path.join(abs_dir, path) for path in args.test]
    gold_swc_file = os.path.join(abs_dir, args.gold)
    gold_file_name = os.path.basename(gold_swc_file)

    # reverse
    reverse = args.reverse
    if reverse is None:
        reverse = True

    # metric
    metric = args.metric
    if metric not in metric_list:
        raise Exception("[Error: ] Unknown metric method {}".format(
            metric
        ))

    # output path
    output_dest = args.output
    if output_dest is not None:
        output_dest = os.path.join(abs_dir, output_dest)
    if output_dest is None:
        output_dest = os.path.join(os.path.join(abs_dir, "output"))
    # config
    config = args.config
    if config is None:
        if platform.system() == "Windows":
            if metric == "diadem_metric" or metric == "DM":
                config = os.path.join(abs_dir, "config\\diadem_metric.json")
            if metric in ["overall_length", "matched_length", "OL", "ML"]:
                config = os.path.join(abs_dir, "config\\length_metric.json")
            if metric in ['volume_metric', 'VM']:
                config = os.path.join(abs_dir, "config\\volume_metric.json")
            if metric in ['branch_metric', "BM"]:
                config = os.path.join(abs_dir, "config\\branch_metric.json")
            if metric in ['link_metric', 'LM']:
                config = os.path.join(abs_dir, "config\\link_metric.json")
        elif platform.system() == "Linux":
            if metric == "diadem_metric" or metric == "DM":
                config = os.path.join(abs_dir, "config/diadem_metric.json")
            if metric in ["overall_length", "matched_length", "OL", "ML"]:
                config = os.path.join(abs_dir, "config/length_metric.json")
            if metric in ['volume_metric', 'VM']:
                config = os.path.join(abs_dir, "config/volume_metric.json")
            if metric in ['branch_metric', "BM"]:
                config = os.path.join(abs_dir, "config/branch_metric.json")
            if metric in ['link_metric', 'LM']:
                config = os.path.join(abs_dir, "config/link_metric.json")

    test_swc_trees, test_tiffs = [], []
    # read test trees, gold trees and configs
    if metric in ['volume_metric', 'VM']:
        for file in test_swc_files:
            test_tiffs += read_tiffs(file)
    else:
        for file in test_swc_files:
            test_swc_trees += read_swc_trees(file)

    gold_swc_trees = read_swc_trees(gold_swc_file)
    config = read_json(config)

    # info: how many trees read
    print("There are {} test image(s) and {} gold image(s)".format(len(test_swc_trees), len(gold_swc_trees)))
    if len(gold_swc_trees) == 0:
        raise Exception("[Error:  ] No gold image detected")
    if len(gold_swc_trees) > 1:
        print("[Warning:  ] More than one gold image detected, only the first one will be used")

    # entries to different metrics
    gold_swc_treeroot = gold_swc_trees[0]
    for test_tiff in test_tiffs:
        if metric == "volume_metric" or metric == "VM":
            recall = volume_metric(tiff_test=test_tiff, swc_gold=gold_swc_treeroot, config=config)
            print(recall)

    for test_swc_treeroot in test_swc_trees:
        if metric == "diadem_metric" or metric == "DM":
            ans = diadem_metric(swc_test_tree=test_swc_treeroot,
                                swc_gold_tree=gold_swc_treeroot,
                                config=config)
            print("score = {}".format(ans[2]))
            if reverse:
                ans_rev = diadem_metric(swc_test_tree=gold_swc_treeroot, swc_gold_tree=test_swc_treeroot, config=config)
                print("rev_score = {}".format(ans_rev[2]))

        if metric == "overall_length" or metric == "OL":
            config["method"] = 1
            lm_res = length_metric(gold_swc_treeroot, test_swc_treeroot,
                                   abs_dir, config)
            if reverse:
                lm_res = length_metric(test_swc_treeroot, gold_swc_treeroot,
                                       abs_dir, config)
                print("Recall = {} Precision = {}".format(lm_res[0], lm_res[1]))

        if metric == "matched_length" or metric == "ML":
            config["method"] = 2
            lm_res = length_metric(gold_swc_treeroot, test_swc_treeroot,
                          abs_dir, config)
            print("Recall = {} Precision = {}".format(lm_res[0], lm_res[1]))

            if output_dest:
                swc_save(test_swc_treeroot, output_dest)
            if reverse:
                config["detail"] = config["detail"][:-4] + "_reverse.swc"
                lm_res = length_metric(test_swc_treeroot, gold_swc_treeroot,
                                       abs_dir, config)
                print("Recall = {} Precision = {}".format(lm_res[0], lm_res[1]))
                if output_dest:
                    swc_save(gold_swc_treeroot, output_dest[:-4]+"_reverse.swc")
        if metric == "branch_metric" or metric == "BM":
            branch_result = branch_leaf_metric(gold_swc_tree=gold_swc_treeroot,
                                               test_swc_tree=test_swc_treeroot,
                                               config=config)
            print("---------------Result---------------")
            print("gole_branch_num = {}, test_branch_num = {}\n"
                  "true_positive_number  = {}\n"
                  "false_negative_num    = {}\n"
                  "false_positive_num    = {}\n"
                  "matched_mean_distance = {}\n"
                  "matched_sum_distance  = {}\n"
                  "pt_score              = {}\n"
                  "isolated node number  = {}".format(branch_result[0], branch_result[1], branch_result[2],
                                                      branch_result[3], branch_result[4], branch_result[5],
                                                      branch_result[6], branch_result[7], branch_result[8]))
            print("----------------End-----------------")
            swc_save(test_swc_treeroot, os.path.join(output_dest,
                                                     "branch_metric",
                                                     "{}{}".format(gold_file_name[:-4], "_test.swc")))
            swc_save(gold_swc_treeroot, os.path.join(output_dest,
                                                     "branch_metric",
                                                     "{}{}".format(gold_file_name[:-4], "_gold.swc")))
        if metric == "link_metric" or metric == "LM":
            edge_loss, tree_dis_loss = link_metric(test_swc_tree=test_swc_treeroot,
                                                   gold_swc_tree=gold_swc_treeroot,
                                                   config=config)
            print("---------------Result---------------")
            print("edge_loss     = {}\n"
                  "tree_dis_loss = {}\n".format(edge_loss, tree_dis_loss))
            print("---------------End---------------")


if __name__ == "__main__":
    sys.exit(run())

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\2_18_test.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\2_18_gold.swc --metric matched_length --reverse true

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\194444.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\194444.swc --metric matched_length --reverse true

# python ./pyneval/cli/pyneval.py --test D:\gitProject\mine\PyNeval\test\data_example\test\194444.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\194444.swc --metric matched_length --reverse true

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem1.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem1.swc --metric diadem_metric

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem7.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem7.swc --metric diadem_metric

# pyneval --gold D:\gitProject\mine\PyNeval\test\data_example\gold\vol_metric\6656_gold.swc --test D:\gitProject\mine\PyNeval\test\data_example\test\vol_metric\6656_2304_22016.pro.tif --metric volume_metric --output D:\gitProject\mine\PyNeval\output\volume_metric\volume_out.swc

# pyneval --gold .\data\branch_metric_data\gold\194444.swc --test .\data\branch_metric_data\test\194444.swc --metric link_metric

# pyneval --gold .\data\branch_metric_data\gold\194444_core.swc --test .\data\branch_metric_data\test\194444_core.swc --metric branch_metric
