import argparse
import sys
import os
import platform
from pyneval.io.read_swc import read_swc_trees
from pyneval.io.read_json import read_json
from pyneval.io.save_swc import swc_save
from pyneval.tools.re_sample import up_sample_swc_tree_command_line, down_sample_swc_tree_command_line

from pyneval.tools.overlap_detect import overlap_clean

method_list = [
    "up_sample",
    "down_sample",
    "overlap_clean",
    "US", "DS", "OC"
]


def read_parameters():
    parser = argparse.ArgumentParser(
        description="pyneval 1.0"
    )
    parser.add_argument(
        "--swc_file",
        "-S",
        help="the route of the test file",
        required=False,
        nargs='*',
    )
    parser.add_argument(
        "--method",
        "-M",
        help="choose a adjust method",
        required=True
    )
    parser.add_argument(
        "--output",
        "-O",
        help="the route of the output file.\nif not specified, output to screen",
        required=True
    )
    parser.add_argument(
        "--config",
        "-C",
        help="special config for different metric method",
        required=False
    )
    parser.add_argument(
        "--debug",
        "-D",
        help="Print debug info or not",
        required=False
    )
    return parser.parse_args()


def run():
    # init path parameter
    abs_dir = os.path.abspath("")
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir, "src"))
    sys.path.append(os.path.join(abs_dir, "test"))
    sys.setrecursionlimit(1000000)

    # read parameter
    args = read_parameters()

    # file paths
    if args.swc_file is None:
        swc_files = []
    else:
        swc_files = [os.path.join(abs_dir, path) for path in args.swc_file]

    # method
    method = args.method
    if method not in method_list:
        raise Exception("[Error: ] Unknown metric method {}".format(
            method
        ))

    # out_path
    out_path = args.output
    # config
    config = args.config
    if config is None:
        if platform.system() == "Windows":
            if method in ["up_sample", "US"]:
                config = os.path.join(abs_dir, "config\\up_sample.json")
            if method in ["down_sample", "DS"]:
                config = os.path.join(abs_dir, "config\\length_metric.json")
            if method in ["overlap_clean", "OC"]:
                config = os.path.join(abs_dir, "config\\overlap_clean.json")
        elif platform.system() == "Linux":
            if method == ["up_sample", "US"]:
                config = os.path.join(abs_dir, "config/diadem_metric.json")
            if method in ["overall_length", "matched_length", "OL", "ML"]:
                config = os.path.join(abs_dir, "config/length_metric.json")
            if method in ["overlap_clean", "OC"]:
                config = os.path.join(abs_dir, "config/overlap_clean.json")
    config = read_json(json_file_path=config)
    tree_name_dict = {}
    swc_trees = []
    for file in swc_files:
        swc_trees += read_swc_trees(file, tree_name_dict=tree_name_dict)

    it = 1
    for swc_tree in swc_trees:
        if method in ["up_sample", "US"]:
            up_sampled_swc_tree = up_sample_swc_tree_command_line(swc_tree=swc_tree, config=config)
            swc_save(swc_tree=up_sampled_swc_tree,
                     out_path=os.path.join(out_path, "up_sampled_" + tree_name_dict[swc_tree]))
        if method in ["down_sample", "DS"]:
            config['stage'] = 0
            down_sampled_swc_tree = down_sample_swc_tree_command_line(swc_tree, config=config)
            config['stage'] = 1
            down_sampled_swc_tree = down_sample_swc_tree_command_line(down_sampled_swc_tree, config=config)
            swc_save(swc_tree=down_sampled_swc_tree, out_path=os.path.join(out_path, "down_sampled_" + tree_name_dict[swc_tree]))
        if method in ["overlap_clean", "OC"]:
            overlap_clean(swc_tree, out_path, tree_name_dict[swc_tree], config)
        it += 1


if __name__ == "__main__":
    sys.exit(run())


# python ./pyneval_tools.py
# --swc_file D:\gitProject\mine\PyNeval\test\data_example\gold\swc_18254_1
# --config D:\gitProject\mine\PyNeval\config\overlap_clean.json
# --method overlap_clean
# --output D:\\gitProject\\mine\\PyNeval\\output\\overlap_clean

# pyneval_tools --swc_file D:\gitProject\mine\PyNeval\test\data_example\gold\swc_18254_1 --config D:\gitProject\mine\PyNeval\config\overlap_clean.json --method overlap_clean --output D:\\gitProject\\mine\\PyNeval\\output\\overlap_clean

# pyneval_tools --swc_file D:\gitProject\mine\PyNeval\test\data_example\gold\2_18_gold.swc --config D:\gitProject\mine\PyNeval\config\down_sample.json --method down_sample --output D:\\gitProject\\mine\\PyNeval\\output\\down_sample

# pyneval_tools --swc_file D:\gitProject\mine\PyNeval\test\data_example\test\2_18_test.swc --config D:\gitProject\mine\PyNeval\config\up_sample.json --method up_sample --output D:\\gitProject\\mine\\PyNeval\\output\\up_sample





