import argparse
import sys,os
from sample.IO_util.read_swc import convert_path_to_binarytree
from sample.metirc.diadem_metric import diadem_reconstruction

def read_parameters():
    parser = argparse.ArgumentParser(
        description="pymet 1.0"
    )

    parser.add_argument(
        "--test",
        "-T",
        help="the route of the test file",
        required=True,
        nargs='*',
    )
    parser.add_argument(
        "--gold",
        "-G",
        help="the route of the gold file",
        required=True
    )
    parser.add_argument(
        "--output",
        "-O",
        help="the route of the output file.\nif not specified, output to screen",
        required=False
    )
    return parser.parse_args()

def pymet():
    abs_dir = os.path.abspath("")
    sys.path.append(abs_dir)
    sys.path.append(os.path.join(abs_dir,"sample"))
    sys.path.append(os.path.join(abs_dir,"test"))

    # args = read_parameters()

    # test_swc_file = args.test
    # gold_swc_file = args.gold
    test_swc_file = "test/data_example/test"
    gold_swc_file = "test/data_example/gold"
    # output_dest = args.output

    test_swc_treeroots = convert_path_to_binarytree(test_swc_file)
    gold_swc_treeroots = convert_path_to_binarytree(gold_swc_file)

    print("There are {} test image(s) and {} gold image(s)".format(len(test_swc_treeroots), len(gold_swc_treeroots)))
    if len(gold_swc_treeroots) == 0:
        raise Exception("[Error:  ] No gold image detected")
    if len(gold_swc_treeroots) > 1:
        print("[Warning:  ] More than one gold image detected, only the first one will be used")

    gold_swc_treeroot = gold_swc_treeroots[0]
    for test_swc_treeroot in test_swc_treeroots:
        print(test_swc_treeroots)
        diadem_reconstruction(test_swc_treeroot, gold_swc_treeroot)

if __name__ == "__main__":
    pymet()