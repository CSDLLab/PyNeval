import argparse
import sys,os,platform
from pyneval.io.read_swc import read_swc_trees, adjust_swcfile
from pyneval.io.read_json import read_json
from pyneval.io.save_swc import swc_save
from pyneval.model.swc_node import SwcTree
from pyneval.metric.diadem_metric import diadem_metric
from pyneval.metric.length_metric import length_metric
from cli.overlap_detect import overlap_clean

metric_list = [
    "diadem_metric",
    "overall_length",
    "matched_length",
    "overlap_clean",
    "DM","OL","ML","OC"
]


def read_parameters():
    parser = argparse.ArgumentParser(
        description="pymet 1.0"
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
def pyneval(DEBUG=True):
    # init path parameter
    abs_dir = os.path.abspath("")
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir, "src"))
    sys.path.append(os.path.join(abs_dir, "test"))

    # read parameter
    args = read_parameters()

    # set config
    # gold/test files
    if args.test is None:
        test_swc_files = []
    else:
        test_swc_files = [os.path.join(abs_dir, path) for path in args.test]
    gold_swc_file = os.path.join(abs_dir, args.gold)

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

    # config
    config = args.config
    if config is None:
        if platform.system() == "Windows":
            if metric == "diadem_metric" or metric == "DM":
                config = os.path.join(abs_dir, "config\\diadem_metric.json")
            if metric in ["overall_length", "matched_length", "OL", "ML"]:
                config = os.path.join(abs_dir, "config\\length_metric.json")
            if metric in ["overlap_clean", "OD"]:
                config = os.path.join(abs_dir, "config\\overlap_clean.json")
        elif platform.system() == "Linux":
            if metric == "diadem_metric" or metric == "DM":
                config = os.path.join(abs_dir, "config/diadem_metric.json")
            if metric in ["overall_length", "matched_length", "OL", "ML"]:
                config = os.path.join(abs_dir, "config/length_metric.json")
            if metric in ["overlap_clean", "OD"]:
                config = os.path.join(abs_dir, "config/overlap_clean.json")
    if DEBUG:
        print("Config = {}".format(config))

    # read test trees, gold trees and configs
    test_swc_trees = []
    for test_swc_file in test_swc_files:
        test_swc_trees += read_swc_trees(test_swc_file)
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


    if metric == "overlap_clean" or metric == "OC":
        # debug
        print("entry")
        print(config["radius_threshold"])
        print(config["length_threshold"])
        print(output_dest)
        overlap_clean(gold_swc_treeroot, output_dest, config)


if __name__ == "__main__":
    pyneval()

# python ./pyneval.py --test D:\gitProject\mine\PyNeval\test\data_example\test\2_18_test.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\2_18_gold.swc --metric matched_length --reverse true

# python ./pyneval.py --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem1.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem1.swc --metric diadem_metric

# python ./pyneval.py --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem7.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem7.swc --metric diadem_metric

# python ./pyneval.py --gold D:\gitProject\mine\PyNeval\test\data_example\gold\overlap\overlap_sample5.swc --metric overlap_clean --output D:\gitProject\mine\PyNeval\output\overlap\overlap_output5.swc
