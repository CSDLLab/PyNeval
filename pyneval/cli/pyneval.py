import argparse
import sys
import os
import platform
import pyneval
from pyneval.io.read_swc import read_swc_trees
from pyneval.io.read_json import read_json
from pyneval.io.save_swc import swc_save
from pyneval.io.read_tiff import read_tiffs
from pyneval.metric.diadem_metric import diadem_metric
from pyneval.metric.length_metric import length_metric
from pyneval.metric.volume_metric import volume_metric
from pyneval.metric.branch_leaf_metric import branch_leaf_metric
from pyneval.metric.link_metric import link_metric
from pyneval.metric import ssd_metric

METRICS = {
    'diadem_metric': {
        'config': "diadem_metric.json",
        'description': "DIADEM metric (https://doi.org/10.1007/s12021-011-9117-y)",
        'alias': ['DM'],
        'public': True
    },
    'ssd_metric': {
        'config': "ssd_metric.json",
        'description': "minimum square error between up-sampled gold and test trees",
        'alias': ['SM'],
        'public': True
    },
    'length_metric': {
        'config': "length_metric.json",
        'description': "length of matched branches and fibers",
        'alias': ['ML'],
        'public': True
    },
    'volume_metric': {
        'config': "volume_metric.json",
        'description': "volume overlap",
        'alias': ['VM'],
        'public': False
    },
    'branch_metric': {
        'config': "branch_metric.json",
        'description': "quality of critical points",
        'alias': ['BM'],
        'public': True
    },
    'link_metric': {
        'config': "link_metric.json",
        'description': "",
        'alias': ['LM'],
        'public': False
    },
}

METRIC_ALIAS_MAP = {}

for metric in METRICS:
    if 'alias' in METRICS[metric]:
        for alias in METRICS[metric]['alias']:
            METRIC_ALIAS_MAP[alias] = metric

def get_root_metric(metric):
    if metric in METRIC_ALIAS_MAP:
        return METRIC_ALIAS_MAP[metric]
    elif metric in METRICS:
        return metric

def get_metric_config(metric):
    return METRICS[get_root_metric(metric)]

def get_metric_summary(with_description):
    summary = ''
    if with_description:
        for metric in METRICS:
            if METRICS[metric].get('public', False):
                description = METRICS[metric]['description']
                summary += '[{}]: '.format(metric) + (description if description else '[No description]') + '\n'
    else:
        summary = ', '.join((filter(lambda m: METRICS[m].get('public', False), METRICS.keys())))

    return summary

config_dir = os.path.join(os.path.dirname(pyneval.__file__), '../config', )

def get_metric_config_path(metric, root_dir):
    return os.path.join(config_dir, get_metric_config(metric)['config'])

def read_parameters():
    parser = argparse.ArgumentParser(
        description="pyneval 1.0"
    )

    parser.add_argument(
        "--test",
        "-T",
        help="a list of SWC files for evaluation",
        required=False,
        nargs='*',
    )
    parser.add_argument(
        "--gold",
        "-G",
        help="path to the gold-standard SWC file",
        required=True
    )
    parser.add_argument(
        "--metric",
        "-M",
        help="metric choice: " + get_metric_summary(False) + ".",
        required=True
    )
    parser.add_argument(
        "--output",
        "-O",
        help="path to the output file (output to screen if not specified)",
        required=False
    )
    parser.add_argument(
        "--config",
        "-C",
        help="custom configuration file for the specified metric",
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
        help="print debug info or not",
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
    try:
        args = read_parameters()
    except:
        return 1

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
    metric = get_root_metric(args.metric)
    if not metric:
        print("\nERROR: The metric '{}' is not supported.".format(args.metric))
        print("\nValid options for --metric:\n")
        print(get_metric_summary(True))
        return 1

    # output path
    output_dest = args.output
    if output_dest is not None:
        output_dest = os.path.join(abs_dir, output_dest)

    # config
    config = args.config
    if config is None:
        config = get_metric_config_path(metric, abs_dir)

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
        if metric == "volume_metric":
            recall = volume_metric(tiff_test=test_tiff, swc_gold=gold_swc_treeroot, config=config)
            print(recall)

    for test_swc_treeroot in test_swc_trees:
        if metric == "diadem_metric":
            ans = diadem_metric(swc_test_tree=test_swc_treeroot,
                                swc_gold_tree=gold_swc_treeroot,
                                config=config)
            print("score = {}".format(ans[2]))
            if reverse:
                ans_rev = diadem_metric(swc_test_tree=gold_swc_treeroot,
                                        swc_gold_tree=test_swc_treeroot,
                                        config=config)
                print("rev_score = {}".format(ans_rev[2]))

        if metric == "ssd_metric":
            ssd_res = ssd_metric.ssd_metric(gold_swc_treeroot, test_swc_treeroot, config)
            print("ssd_score = {}\n"
                  "recall    = {}\n"
                  "precision = {}\n".format(ssd_res[0], ssd_res[1], ssd_res[2]))

        if metric == "length_metric":
            lm_res = length_metric(gold_swc_treeroot, test_swc_treeroot, config)
            print("Recall = {} Precision = {}".format(lm_res[0], lm_res[1]))

            if output_dest:
                swc_save(test_swc_treeroot, output_dest)
            if reverse:
                if "detail" in config:
                    config["detail"] = config["detail"][:-4] + "_reverse.swc"
                lm_res = length_metric(test_swc_treeroot, gold_swc_treeroot, config)
                print("Recall = {} Precision = {}".format(lm_res[0], lm_res[1]))
                if output_dest:
                    swc_save(gold_swc_treeroot, output_dest[:-4]+"_reverse.swc")
        if metric == "branch_metric":
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
            if os.path.exists(output_dest):
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

# pyneval --gold .\\data\test_data\topo_metric_data\gold_fake_data1.swc --test .\data\test_data\topo_metric_data\test_fake_data1.swc --metric link_metric

# pyneval --gold .\\data\\test_data\\ssd_data\\gold\\a.swc --test .\\data\\test_data\\ssd_data\\test\\a.swc --metric branch_metric

# pyneval --gold .\\data\test_data\geo_metric_data\gold_34_23_10.swc --test .\data\test_data\geo_metric_data\test_34_23_10.swc --metric ssd_metric
