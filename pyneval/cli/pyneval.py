import argparse
import sys
import os
import jsonschema
import pyneval
from pyneval.io.read_swc import read_swc_trees
from pyneval.io import read_json
from pyneval.io.swc_writer import swc_save
from pyneval.io.read_tiff import read_tiffs
from pyneval.metric import diadem_metric
from pyneval.metric import length_metric
from pyneval.metric import volume_metric
from pyneval.metric import branch_leaf_metric
from pyneval.metric import link_metric
from pyneval.metric import ssd_metric

METRICS = {
    'diadem_metric': {
        'config': "diadem_metric.json",
        'description': "DIADEM metric (https://doi.org/10.1007/s12021-011-9117-y)",
        'alias': ['DM'],
        'method': diadem_metric.diadem_metric,
        'public': True
    },
    'ssd_metric': {
        'config': "ssd_metric.json",
        'description': "minimum square error between up-sampled gold and test trees",
        'alias': ['SM'],
        'method': ssd_metric.ssd_metric,
        'public': True
    },
    'length_metric': {
        'config': "length_metric.json",
        'description': "length of matched branches and fibers",
        'alias': ['ML'],
        'method': length_metric.length_metric,
        'public': True
    },
    'volume_metric': {
        'config': "volume_metric.json",
        'description': "volume overlap",
        'alias': ['VM'],
        'method': volume_metric.volume_metric,
        'public': False
    },
    'branch_metric': {
        'config': "branch_metric.json",
        'description': "quality of critical points",
        'alias': ['BM'],
        'method': branch_leaf_metric.branch_leaf_metric,
        'public': True
    },
    'link_metric': {
        'config': "link_metric.json",
        'description': "",
        'alias': ['LM'],
        'method': link_metric.link_metric,
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

def get_metric_config_schema_path(metric, root_dir):
    schema_dir = os.path.join(config_dir, "schemas")
    return os.path.join(schema_dir, get_metric_config(metric)['config'][:-5]+"_schema.json")

def get_metric_method(metric):
    return get_metric_config(metric)['method']

def read_parameters():
    parser = argparse.ArgumentParser(
        description="pyneval 1.0"
    )

    parser.add_argument(
        "--gold",
        "-G",
        help="path to the gold-standard SWC file",
        required=True
    )
    parser.add_argument(
        "--test",
        "-T",
        help="a list of SWC files for evaluation",
        required=True,
        nargs='*',
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
        help="metric output path, including different scores of the metric",
        required=False
    )
    parser.add_argument(
        "--detail",
        "-D",
        help="detail \"type\" marked for gold/test SWC file, including marked swc trees",
        required=False
    )
    parser.add_argument(
        "--config",
        "-C",
        help="custom configuration file for the specified metric",
        required=False
    )
    parser.add_argument(
        "--debug",
        help="print debug info or not",
        required=False
    )
    return parser.parse_args()


def init(abs_dir):
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir, "src"))
    sys.path.append(os.path.join(abs_dir, "test"))
    sys.setrecursionlimit(1000000)


def set_configs(abs_dir, args):
    # argument: gold
    gold_swc_path = os.path.join(abs_dir, args.gold)
    if not (os.path.isfile(gold_swc_path) and gold_swc_path[-4:] == ".swc"):
        raise Exception("[Error: ] gold standard file is not a swc file")
    gold_swc_tree = read_swc_trees(gold_swc_path)[0]  # SwcTree

    # argument: metric
    metric = get_root_metric(args.metric)
    if not metric:
        print("\nERROR: The metric '{}' is not supported.".format(args.metric))
        print("\nValid options for --metric:\n")
        print(get_metric_summary(True))
        return 1

    # argument: test
    test_swc_paths = [os.path.join(abs_dir, path) for path in args.test]
    test_swc_trees = []
    # read test trees
    if metric in ['volume_metric', 'VM']:
        for file in test_swc_paths:
            test_swc_trees += read_tiffs(file)
    else:
        for file in test_swc_paths:
            test_swc_trees += read_swc_trees(file)

    # info: how many trees read
    print("There are {} test image(s)".format(len(test_swc_trees)))

    # argument: output
    output_dir = None
    if args.output:
        output_dir = os.path.join(abs_dir, args.output)

    # argument: detail
    detail_dir = None
    if args.detail:
        detail_dir = os.path.join(abs_dir, args.detail)

    # argument: config
    config_path = args.config
    if config_path is None:
        config_path = get_metric_config_path(metric, abs_dir)
    config_schema_path = get_metric_config_schema_path(metric, abs_dir)

    config = read_json.read_json(config_path)
    config_schema = read_json.read_json(config_schema_path)
    try:
        jsonschema.validate(config, config_schema)
    except Exception:
        raise Exception("[Error: ]Error in analyzing config json file")

    # argument: debug
    is_debug = args.debug

    return gold_swc_tree, test_swc_trees, metric, output_dir, detail_dir, config, is_debug


def excute_metric(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_dir, file_name_extra=""):
    metric_method = get_metric_method(metric)
    test_swc_name = test_swc_tree.get_name()
    gold_swc_name = gold_swc_tree.get_name()

    result = metric_method(gold_swc_tree=gold_swc_tree, test_swc_tree=test_swc_tree, config=config)

    print("---------------Result---------------")
    for key in result:
        print("{} = {}".format(key.ljust(15, ' '), result[key]))
    print("----------------End-----------------\n")

    if file_name_extra == "reverse":
        file_name = gold_swc_name[:-4] + "_" + metric + "_" + file_name_extra + ".swc"
    else:
        file_name = test_swc_name[:-4] + "_" + metric + "_" + file_name_extra + ".swc"

    if detail_dir:
        swc_save(swc_tree=gold_swc_tree,
                 out_path=os.path.join(detail_dir, file_name))

    if output_dir:
        read_json.save_json(data=result,
                            json_file_path=os.path.join(output_dir, file_name))


# command program
def run():
    abs_dir = os.path.abspath("")
    init(abs_dir)

    try:
        args = read_parameters()
    except:
        raise Exception("[Error: ] Error in reading parameters")
    gold_swc_tree, test_swc_trees, metric, output_dir, detail_dir, config, is_debug = set_configs(abs_dir, args)

    for test_swc_tree in test_swc_trees:
        excute_metric(metric=metric, gold_swc_tree=gold_swc_tree, test_swc_tree=test_swc_tree,
                      config=config, detail_dir=detail_dir, output_dir=output_dir)
        if metric in ["length_metric", "diadem_metric"]:
            excute_metric(metric=metric, gold_swc_tree=test_swc_tree, test_swc_tree=gold_swc_tree,
                          config=config, detail_dir=detail_dir, output_dir=output_dir, file_name_extra="reverse")


if __name__ == "__main__":
    sys.exit(run())

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\2_18_test.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\2_18_gold.swc --metric matched_length --reverse true

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\194444.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\194444.swc --metric matched_length --reverse true

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem1.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem1.swc --metric diadem_metric

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem7.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem7.swc --metric diadem_metric

# pyneval --gold .\\data\example_selected\g.swc --test .\\data\example_selected\g.tif --metric volume_metric --output D:\gitProject\mine\PyNeval\output\volume_metric\volume_out.swc

# pyneval --gold .\\data\test_data\topo_metric_data\gold_fake_data1.swc --test .\data\test_data\topo_metric_data\test_fake_data1.swc --metric link_metric

# pyneval --gold .\\data\\test_data\\ssd_data\\gold\\a.swc --test .\\data\\test_data\\ssd_data\\test\\a.swc --metric branch_metric

# pyneval --gold .\\data\test_data\geo_metric_data\gold_34_23_10.swc --test .\data\test_data\geo_metric_data\test_34_23_10.swc --metric branch_metric

# pyneval --gold ./data/test_data/geo_metric_data/gold_fake_data1.swc --test ./data/test_data/geo_test/ --metric branch_metric --detail ./output
