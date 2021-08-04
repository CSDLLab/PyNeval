"""
    This is a comprehensive test for PyNeval.
    It includes several basic tests on each metric.
    Every time before merging a branch, committer should run this test and make sure every case is passed.
    If the changes in the commit will change the output, i.e., a debug commit, committer should edit this file synchronously.
"""
import os
import sys

import jsonschema
from pyneval.cli import pyneval
from pyneval.model import swc_node
from pyneval.io import read_json
from pyneval.metric.utils import config_utils
from pyneval.metric.utils import metric_manager
from multiprocessing import Pool, cpu_count

STD_TEST_DATA_PATH = "../../data/std_test_data"
abs_dir = os.path.abspath("../../")
pyneval.import_metrics(abs_dir)


def res_compare(metric_name, file_name, test, std):
    OK_FLAG = True
    for key in test:
        if test[key] != std[key]:
            print("[Wrong Answer]:\nmetric name: {}\nfile name: {}\nindex name: {}\nstd answer: {}\noutput answer: {}".format(
                metric_name, file_name, key, std[key], test[key]
            ))
            OK_FLAG = False
    return OK_FLAG


def std_test(mode=1):
    metric_names = ["ssd", "length", "diadem", "critical_node"]
    ok_num, tot_num = 0, 0
    local_metric_manager = metric_manager.get_metric_manager()

    # for each metric
    for metric_name in metric_names:
        print("[INFO]: Testing Metric: {}".format(metric_name))
        metric_method = local_metric_manager.get_metric_method(metric_name)
        metric_ok_num, metric_tot_num = 0, 0

        # for each file in STD_TEST_DATA_PATH
        # max_procs = cpu_count()
        # results = []
        # p_pool = Pool(max_procs)
        for file_name in os.listdir(STD_TEST_DATA_PATH):
            # print("[INFO]: Testing File: {}".format(file_name))
            # loading the trees
            gold_path = os.path.join(STD_TEST_DATA_PATH, file_name, "gold.swc")
            test_path = os.path.join(STD_TEST_DATA_PATH, file_name, "test.swc")
            gold_tree = swc_node.SwcTree()
            test_tree = swc_node.SwcTree()
            gold_tree.load(gold_path)
            test_tree.load(test_path)
            # loading config
            config = config_utils.get_default_configs(metric_name)
            config_schema = config_utils.get_config_schema(metric_name)
            try:
                jsonschema.validate(config, config_schema)
            except Exception as e:
                raise Exception("[Error: ]Error in analyzing config json file")
            # do evaluation
            res = metric_method(gold_tree, test_tree, config)[0]
            # choice: save metric results or compare with the existing results
            std_path = os.path.join(STD_TEST_DATA_PATH, file_name, "std_{}.json".format(metric_name))
            if mode == 2:
                read_json.save_json(std_path, res)
            else:
                std = read_json.read_json(std_path)
                if res_compare(
                        file_name=file_name,
                        metric_name=metric_name,
                        test=res,
                        std=std
                ):
                    ok_num += 1
                    metric_ok_num += 1
            tot_num += 1
            metric_tot_num += 1
        print("        Passed test case: {}\n"
              "        Total test case: {}".format(metric_ok_num, metric_tot_num))
    print("[INFO]: Overall Result:\n"
          "        Passed test case: {}\n"
          "        Total test case: {}".format(ok_num, tot_num))


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    std_test(mode=1)
