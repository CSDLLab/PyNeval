import argparse
import importlib
import os
import platform
import sys
from multiprocessing import Pool, cpu_count

import jsonschema
from pyneval.errors.exceptions import InvalidMetricError, PyNevalError
from pyneval.io import read_json
from pyneval.io.read_swc import read_swc_tree, read_swc_trees
from pyneval.io.read_tiff import read_tiffs
from pyneval.io.swc_writer import swc_save
from pyneval.metric.utils import anno_utils, config_utils
from pyneval.metric.utils.metric_manager import get_metric_manager
from pyneval.tools.optimize import optimize


# load method in metrics
def import_metrics(abs_path):
    metric_path = os.path.join(abs_path, "pyneval/metric")
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

    parser = argparse.ArgumentParser(description="pyneval 1.0")

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


def check_path(path_name, dir_path):
    while not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(
            "The input path {} for {} does not exist or is not a folder. You may choose to:\n"
            "[Input=1]Input a new path\n"
            "[Input=2]Quit this process\n"
            "[Input=3]Continue without saving".format(dir_path, path_name)
        )
        if not os.path.isfile(dir_path):
            print("[Input=4]Create new folder {}.".format(dir_path))
        choice = input()
        if choice.lower() == "1":
            print("Input new detail path:")
            new_dir = input()
            return 1, new_dir
        elif choice.lower() == "2":
            print("Pyneval ends...")
            return 2, ""
        elif choice.lower() == "3":
            print("Pyneval processing without saving details ...")
            return 3, ""
        elif choice.lower() == "4":
            if os.path.isfile(dir_path):
                print("[Info: ] Error input")
                continue
            os.makedirs(dir_path)
            print("{} has been created".format(dir_path))
            return 4, ""
        else:
            print("[Info: ] Error input")
    return 4, ""


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
        raise PyNevalError("test images can't be null")

    # info: how many trees read
    print("There are {} test image(s) \n".format(len(test_swc_trees)))

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
        choose, new_path = check_path("output", output_dir)
        if choose == 1:
            output_dir = new_path
        elif choose == 2:
            raise Exception("Pyneval end by user")
        elif choose == 3:
            output_dir = None

    # argument: detail
    detail_dir = None
    if args.detail:
        detail_dir = os.path.join(abs_dir, args.detail)
        choose, new_path = check_path("detail", detail_dir)
        if choose == 1:
            detail_dir = new_path
        elif choose == 2:
            raise Exception("Pyneval end by user")
        elif choose == 3:
            detail_dir = None

    # argument: parallel
    is_parallel = False
    if args.parallel:
        is_parallel = args.parallel

    # argument: optimize
    optimize_config = None
    if args.optimize:
        optimize_config = read_json.read_json(args.optimize)

    return gold_swc_tree, test_swc_trees, test_swc_paths, metric, output_dir, detail_dir, config, is_debug, is_parallel, optimize_config


def excute_metric(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_dir, metric_method):
    test_swc_name = test_swc_tree.get_name()

    result, res_gold_swc_tree, res_test_swc_tree = metric_method(
        gold_swc_tree=gold_swc_tree, test_swc_tree=test_swc_tree, config=config
    )
    result_info = ""
    for key in result:
        result_info += "{} = {}\n".format(key.ljust(15, " "), result[key])

    print("---------------Result---------------\n" +
          "swc_file_name   = {}\n".format(test_swc_name) +
          result_info +
          "----------------End-----------------\n"
          )

    file_name = test_swc_name[:-4] + "_" + metric + "_"

    if detail_dir:
        if res_gold_swc_tree is not None:
            swc_save(
                swc_tree=res_gold_swc_tree,
                out_path=os.path.join(detail_dir, file_name + "recall.swc"),
                extra=anno_utils.get_detail_type(metric),
            )
        if res_test_swc_tree is not None:
            swc_save(
                swc_tree=res_test_swc_tree,
                out_path=os.path.join(detail_dir, file_name + "precision.swc"),
                extra=anno_utils.get_detail_type(metric),
            )

    if output_dir:
        read_json.save_json(data=result, json_file_path=os.path.join(output_dir, file_name + ".json"))

# command program
def run():
    abs_dir = os.path.abspath("")
    import_metrics(abs_dir)
    init(abs_dir)

    args = read_parameters()
    gold_swc_tree, test_swc_trees, test_swc_paths, metric, output_dir, detail_dir, \
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
                args=(metric, gold_swc_tree, test_swc_tree, config, detail_dir, output_dir, metric_method),
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
                output_dir=output_dir,
                metric_method=metric_method,
            )
    print("All Finished!")


if __name__ == "__main__":
    sys.exit(run())

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\2_18_test.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\2_18_gold.swc --metric matched_length --reverse true

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\194444.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\194444.swc --metric matched_length --reverse true

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem1.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem1.swc --metric diadem_metric

# pyneval --test D:\gitProject\mine\PyNeval\test\data_example\test\diadem\diadem7.swc --gold D:\gitProject\mine\PyNeval\test\data_example\gold\diadem\diadem7.swc --metric diadem_metric

# pyneval --gold .\\data\example_selected\g.swc --test .\\data\example_selected\g.tif --metric volume_metric --output D:\gitProject\mine\PyNeval\output\volume_metric\volume_out.swc

# pyneval --gold .\\data\test_data\topo_metric_data\gold_fake_data1.swc --test .\data\test_data\topo_metric_data\test_fake_data1.swc --metric link_metric

# pyneval --gold .\\data\\test_data\\ssd_data\\gold\\a.swc --test .\\data\\test_data\\ssd_data\\test\\a.swc --metric critical_node_metric

# pyneval --gold .\\data\test_data\geo_metric_data\gold_34_23_10.swc --test .\data\test_data\geo_metric_data\test_34_23_10.swc .\data\test_data\geo_metric_data\test_34_23_10.swc --metric cn
