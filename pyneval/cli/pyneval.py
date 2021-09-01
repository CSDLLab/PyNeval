import argparse
import importlib
import os
import sys
import jsonschema
import pkg_resources

from multiprocessing import Pool, cpu_count
from pyneval.errors.exceptions import InvalidMetricError, PyNevalError
from pyneval.io import read_json
from pyneval.io.read_swc import read_swc_tree, read_swc_trees
from pyneval.io.swc_writer import swc_save
from pyneval.metric.utils import anno_utils, config_utils
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

    parser.add_argument("--debug", help="print debug info or not", required=False, action="store_true")

    return parser.parse_args()


def init(abs_dir):
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir, "src"))
    sys.path.append(os.path.join(abs_dir, "test"))
    sys.setrecursionlimit(1000000)


# def check_dir(dir_name, dir):
#     while not os.path.exists(dir) or not os.path.isdir(dir):
#         print(
#             "The input path {} for {} does not exist or is not a folder. You may choose to:\n"
#             "[Input=1]Input a new path\n"
#             "[Input=2]Quit this process\n"
#             "[Input=3]Continue without saving\n"
#             "[Input=4]Create new folder {}.".format(dir, dir_name, dir)
#         )
#         choice = input()
#         if choice.lower() == "1":
#             print("Input new detail path:")
#             new_dirorpath = input()
#             if new_dirorpath[-5:] == ".json":
#                 new_dir = os.path.dirname(new_dirorpath)
#             else:
#                 new_dir = new_dirorpath
#             if os.path.exists(new_dir) and os.path.isdir(new_dir):
#                 return 1, new_dirorpath
#             else:
#                 dir = new_dir
#                 continue
#         elif choice.lower() == "2":
#             print("Pyneval ends...")
#             return 2, ""
#         elif choice.lower() == "3":
#             print("Pyneval processing without saving {}...".format(dir_name))
#             return 3, ""
#         elif choice.lower() == "4":
#             if os.path.isfile(dir):
#                 print("[Info: ] Error input")
#                 continue
#             os.makedirs(dir)
#             print("{} has been created".format(dir))
#             return 4, ""
#         else:
#             print("[Info: ] Error input")
#     return 4, ""


def set_configs(abs_dir, args):
    # argument: debug
    is_debug = False
    if args.debug and args.debug.lower() in ("true", "t", "yes"):
        is_debug = True

    # argument: gold
    gold_swc_path = os.path.join(abs_dir, args.gold)
    gold_swc_tree = read_swc_tree(gold_swc_path)  # SwcTree

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
        test_swc_trees.extend(read_swc_trees(file))


    if len(test_swc_paths) == 0:
        raise PyNevalError("test models can't be null")

    # info: how many trees read
    print("Evaluating {} test model(s) \n".format(len(test_swc_trees)))

    # argument: config
    config_path = args.config
    if config_path is None:
        config = config_utils.get_default_configs(metric)
    else:
        config = read_json.read_json(config_path)

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

    # argument: optimize
    optimize_config = None
    if args.optimize:
        optimize_config = read_json.read_json(args.optimize)

    return gold_swc_tree, test_swc_trees, test_swc_paths, metric, output_path, detail_dir, config, is_debug, is_parallel, optimize_config


def excute_metric(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_path, metric_method):
    test_swc_name = test_swc_tree.get_name()

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
        ok = swc_save(
            swc_tree=swc_tree,
            out_path=os.path.join(detail_dir, file_name),
            extra=anno_utils.get_detail_type(metric),
        )
        if ok:
            print("[Info:] Details: {} saved".format(file_name))
        else:
            print("[Warning:] Failed to save details: {}".format(file_name))

    if detail_dir:
        if res_gold_swc_tree is not None:
            save_detail(res_gold_swc_tree, base_file_name+"recall.swc")

        if res_test_swc_tree is not None:
            save_detail(res_test_swc_tree, base_file_name+"precision.swc")

    if output_path:
        ok = read_json.save_json(data=result, json_file_path=output_path)
        if ok:
            print("[Info:] Output saved")
        else:
            print("[Warning:] Failed to save output")


# command program
def run():
    abs_dir = os.path.abspath("")
    import_metrics()
    init(abs_dir)

    args = read_parameters()
    gold_swc_tree, test_swc_trees, test_swc_paths, metric, output_path, detail_dir, \
    config, is_debug, is_parallel, optimize_config = set_configs(abs_dir, args)

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
                args=(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_path, metric_method),
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
            )
    print("Done!")


if __name__ == "__main__":
    sys.exit(run())
