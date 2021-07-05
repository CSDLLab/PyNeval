import argparse
import sys
import os
import jsonschema
import importlib
import pyneval

from pyneval.io.read_swc import read_swc_trees
from pyneval.io import read_json
from pyneval.io.swc_writer import swc_save
from pyneval.io.read_tiff import read_tiffs
from pyneval.metric.utils import anno_utils
from pyneval.metric.utils import config_utils
from pyneval.metric.metric_manager import get_metric_manager

# load method in metrics
def import_metrics(abs_path):
    metric_path = os.path.join(abs_path, "pyneval/metric")
    files= os.listdir(metric_path)
    metrics = []
    for f in files:
        if f in ('__init__.py', 'metric_manager.py'):
            continue
        m_f = f.split(".")
        if len(m_f) == 2 and m_f[1] == 'py':
            metrics.append(m_f[0])
    for m in metrics:
        md = 'pyneval.metric.{}'.format(m)
        importlib.import_module(md)


def read_parameters():
    metric_manager = get_metric_manager()

    parser = argparse.ArgumentParser(
        description="pyneval 1.0"
    )

    parser.add_argument(
        "--gold",
        "-G",
        help="path of the gold standard SWC file",
        required=False
    )
    parser.add_argument(
        "--test",
        "-T",
        help="a list of reconstructed SWC files or folders for evaluation",
        required=False,
        nargs='*',
    )
    parser.add_argument(
        "--metric",
        "-M",
        help="metric choice: " + metric_manager.get_metric_summary(False) + ".",
        required=False
    )
    parser.add_argument(
        "--output",
        "-O",
        help="output path of metric results, output file is in json format with different scores of the metric",
        required=False
    )
    parser.add_argument(
        "--detail",
        "-D",
        help="output path of detail metric result, swc format presented.\n"
             "identify different type according to metric result for each node",
        required=False
    )
    parser.add_argument(
        "--config",
        "-C",
        help="path of custom configuration file for the specified metric",
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
    metric_manager = get_metric_manager()
    metric = metric_manager.get_root_metric(args.metric)
    if not metric:
        raise Exception("\nERROR: The metric '{}' is not supported.".format(args.metric) +
                        "\nValid options for --metric:\n" +
                        metric_manager.get_metric_summary(True))

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

    # argument: config
    config_path = args.config
    if config_path is None:
        config = config_utils.get_default_configs(metric)
    else:
        config = read_json.read_json(config_path)

    config_schema = config_utils.get_config_schema(metric)
    jsonschema.validate(config, config_schema)

    # argument: output
    output_dir = None
    if args.output:
        output_dir = os.path.join(abs_dir, args.output)

    # argument: detail
    detail_dir = None
    if args.detail:
        detail_dir = os.path.join(abs_dir, args.detail)
        config["detail"] = True

    # argument: debug
    is_debug = args.debug

    return gold_swc_tree, test_swc_trees, metric, output_dir, detail_dir, config, is_debug


def excute_metric(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_dir):
    metric_manager = get_metric_manager()
    metric_method = metric_manager.get_metric_method(metric)
    test_swc_name = test_swc_tree.get_name()

    result, res_gold_swc_tree, res_test_swc_tree = metric_method(gold_swc_tree=gold_swc_tree,
                                                                 test_swc_tree=test_swc_tree, config=config)

    print("---------------Result---------------")
    for key in result:
        print("{} = {}".format(key.ljust(15, ' '), result[key]))
    print("----------------End-----------------\n")

    file_name = test_swc_name[:-4] + "_" + metric + "_"

    if detail_dir:
        if res_gold_swc_tree is not None:
            swc_save(swc_tree=res_gold_swc_tree,
                     out_path=os.path.join(detail_dir, file_name + "recall.swc"),
                     extra=anno_utils.get_detail_type(metric))
        if res_test_swc_tree is not None:
            swc_save(swc_tree=res_test_swc_tree,
                     out_path=os.path.join(detail_dir, file_name + "precision.swc"),
                     extra=anno_utils.get_detail_type(metric))

    if output_dir:
        read_json.save_json(data=result,
                            json_file_path=os.path.join(output_dir, file_name + ".json"))


# command program
def run():
    abs_dir = os.path.abspath("")
    import_metrics(abs_dir)
    init(abs_dir)

    args = read_parameters()
    gold_swc_tree, test_swc_trees, metric, output_dir, detail_dir, config, is_debug = set_configs(abs_dir, args)

    for test_swc_tree in test_swc_trees:
        excute_metric(metric=metric, gold_swc_tree=gold_swc_tree, test_swc_tree=test_swc_tree,
                      config=config, detail_dir=detail_dir, output_dir=output_dir)


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
