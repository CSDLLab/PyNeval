import argparse
import importlib
import os
import sys
import jsonschema
import pkg_resources

from multiprocessing import Pool, cpu_count
from pyneval.errors.exceptions import InvalidMetricError, PyNevalError
from pyneval.pyneval_io import json_io
from pyneval.pyneval_io import swc_io
from pyneval.metric.utils import anno_utils, config_utils
from pyneval.metric.utils import cli_utils
from pyneval.metric.utils.metric_manager import get_metric_manager
from pyneval.tools.optimize import optimize

# load method in metrics
def import_metrics():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    metric_path = os.path.join(base_dir, "pyneval/metric")
    files = os.listdir(metric_path)
    metrics = []
    for f in files:
        m_f = f.split(".")
        if len(m_f) == 2 and m_f[0][-7:] == "_metric" and m_f[1] == "py":
            metrics.append(m_f[0])
    for m in metrics:
        md = "pyneval.metric.{}".format(m)
        importlib.import_module(md)


def read_parameters():
    metric_manager = get_metric_manager()

    parser = argparse.ArgumentParser(description="Current version: pyneval {}".format(
        pkg_resources.require("pyneval")[0].version)
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
        nargs="*"
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
        required=False,
    )
    parser.add_argument(
        "--detail",
        "-D",
        help="output path of detail metric result, swc format presented.\n"
             "identify different type according to metric result for each node",
        required=False,
    )
    parser.add_argument(
        "--config",
        "-C",
        help="path of custom configuration file for the specified metric",
        required=False,
    )
    parser.add_argument(
        "--parallel",
        "-P",
        help="Enable the parallel processing",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "--optimize",
        help="Enable optimizer mode",
        required=False,
    )
    parser.add_argument(
        "--path_validation",
        help="Enable detailed path validation check",
        required=False,
        action="store_true"
    )
    parser.add_argument("--debug", help="print debug info or not", required=False, action="store_true")

    return parser.parse_args()


def init(abs_dir):
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir, "src"))
    sys.path.append(os.path.join(abs_dir, "test"))
    sys.setrecursionlimit(1000000)


def set_configs(abs_dir, args):
    # argument: debug
    is_debug = False
    if args.debug and args.debug.lower() in ("true", "t", "yes"):
        is_debug = True

    # argument: gold
    gold_swc_path = os.path.join(abs_dir, args.gold)
    gold_swc_tree = swc_io.read_swc_tree(gold_swc_path)  # SwcTree

    # argument: metric
    metric_manager = get_metric_manager()
    metric = metric_manager.get_root_metric(args.metric)
    if not metric:
        raise InvalidMetricError(args.metric, metric_manager.get_metric_summary(True))

    # argument: test
    test_swc_paths = [os.path.join(abs_dir, path) for path in args.test]
    test_swc_trees = []
    # read test trees
    for file in test_swc_paths:
        if file[-4:].lower() == ".tif":
            continue
        test_swc_trees.extend(swc_io.read_swc_trees(file))

    if len(test_swc_paths) == 0:
        raise PyNevalError("test models can't be null")

    # info: how many trees read
    print("Evaluating {} test model(s) \n".format(len(test_swc_trees)))

    # argument: config
    config_path = args.config
    if config_path is None:
        config = config_utils.get_default_configs(metric)
    else:
        config = json_io.read_json(config_path)

    config_schema = config_utils.get_config_schema(metric)
    jsonschema.validate(config, config_schema)

    # argument: output
    output_path = None
    if args.output:
        output_path = os.path.join(abs_dir, args.output)

    # argument: detail
    detail_dir = None
    if args.detail:
        detail_dir = os.path.join(abs_dir, args.detail)

    # argument: parallel
    is_parallel = False
    if args.parallel:
        is_parallel = args.parallel

    is_path_validation = False
    if args.path_validation:
        is_path_validation = args.path_validation

    # argument: optimize
    optimize_config = None
    if args.optimize:
        optimize_config = json_io.read_json(args.optimize)

    return gold_swc_tree, test_swc_trees, test_swc_paths, metric, output_path, detail_dir, config, is_debug, is_parallel, optimize_config, is_path_validation


def excute_metric(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_path, metric_method, is_path_validation):
    test_swc_name = test_swc_tree.name()

    result, res_gold_swc_tree, res_test_swc_tree = metric_method(
        gold_swc_tree=gold_swc_tree, test_swc_tree=test_swc_tree, config=config
    )
    screen_output = config_utils.get_screen_output()
    result_info = ""
    for key in result:
        if key in screen_output[metric]:
            result_info += "{} = {}\n".format(key.ljust(15, " "), result[key])

    print("---------------Result---------------\n" +
          "swc_file_name   = {}\n".format(test_swc_name) +
          result_info +
          "----------------End-----------------\n"
          )

    base_file_name = test_swc_name[:-4] + "_" + metric + "_"

    def save_detail(swc_tree, file_name):
        detail_path = os.path.normpath(os.path.join(detail_dir, file_name))
        if is_path_validation:
            detail_path = cli_utils.path_validation(detail_path, ".swc")
        else:
            detail_path = cli_utils.make_sure_path_not_exist(detail_path)
        ok = False
        if detail_path is not None:
            ok = swc_io.swc_save(
                swc_tree=swc_tree,
                out_path=detail_path,
                extra=anno_utils.get_detail_type(metric),
            )
        if detail_path is None or not ok:
            print("[Warning:] Failed to save details: {}".format(file_name))

    if detail_dir:
        if res_gold_swc_tree is not None:
            save_detail(res_gold_swc_tree, base_file_name+"recall.swc")

        if res_test_swc_tree is not None:
            save_detail(res_test_swc_tree, base_file_name+"precision.swc")

    if output_path:
        if is_path_validation:
            output_path = cli_utils.path_validation(output_path, ".json")
        else:
            output_path = cli_utils.make_sure_path_not_exist(output_path)
        ok = False
        if output_path is not None:
            ok = json_io.save_json(data=result, json_file_path=output_path)
            if ok:
                print("[Info:] Output saved")
        if output_path is None or not ok:
            print("[Warning:] Failed to save output")


# command program
def run():
    abs_dir = os.path.abspath("")
    import_metrics()
    init(abs_dir)

    args = read_parameters()
    gold_swc_tree, test_swc_trees, test_swc_paths, metric, output_path, detail_dir, \
    config, is_debug, is_parallel, optimize_config, is_path_validation = set_configs(abs_dir, args)

    metric_manager = get_metric_manager()
    metric_method = metric_manager.get_metric_method(metric)

    if optimize_config is not None:
        optimize.optimize(gold_swc_tree=gold_swc_tree, test_swc_paths=test_swc_paths,
                          optimize_config=optimize_config, metric_config=config, metric_method=metric_method)
    elif is_parallel:
        # use multi process
        max_procs = cpu_count()
        if len(test_swc_trees) < max_procs:
            max_procs = len(test_swc_trees)
        p_pool = Pool(max_procs)
        for test_swc_tree in test_swc_trees:
            p_pool.apply_async(
                excute_metric,
                args=(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_path, metric_method, is_path_validation),
            )
        p_pool.close()
        p_pool.join()
    else:
        for test_swc_tree in test_swc_trees:
            excute_metric(
                metric=metric,
                gold_swc_tree=gold_swc_tree,
                test_swc_tree=test_swc_tree,
                config=config,
                detail_dir=detail_dir,
                output_path=output_path,
                metric_method=metric_method,
                is_path_validation=is_path_validation,
            )
    print("Done!")


if __name__ == "__main__":
    sys.exit(run())
