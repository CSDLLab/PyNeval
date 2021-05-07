import os

from pyneval.tools.optimize.SA import SAFast
from pyneval.metric import ssd_metric
from pyneval.model import swc_node
from pyneval.io import read_json
from scipy import stats as st

import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

g_score = -1
g_gold_tree = None
g_tar_tree = None
g_rcn_method = None
g_rcn_config = None
g_metric_method = None
g_metric_configs = None

NEUTU_PATH = "../../../../../00_program_file/00_neutu/bin/neutu"
ORIGIN_PATH = "../../../data/optimation/test1/test1_test.tif"
GOLD_PATH = "../../../data/optimation/test1/test1_gold.swc"
TEST_PATH = "../../../data/optimation/output/"
CONFIG_PATH = "../../../config/fake_reconstruction_configs/"
METRIC_CONFIG_PATH = "../../../config/ssd_metric.json"
LOG_PATH = "../../../output/optimization/neutu_log.txt"


def SA_optimize(configs=None, test_name=None, lock=None):
    global g_metric_method
    global g_metric_configs
    global g_rcn_config

    LOC_CONFIG_PATH = os.path.join(CONFIG_PATH, test_name+".json")
    LOC_TEST_PATH = os.path.join(TEST_PATH, test_name+".swc")
    rec_config = copy.deepcopy(g_rcn_config)

    if configs is not None:
        rec_config["trace"]["default"]["minimalScoreAuto"] = configs[0]
        rec_config["trace"]["default"]["minimalScoreManual"] = configs[1]
        rec_config["trace"]["default"]["minimalScoreSeed"] = configs[2]
        rec_config["trace"]["default"]["minimalScore2d"] = configs[3]

        read_json.save_json(LOC_CONFIG_PATH, rec_config)

    REC_CMD = "{} --command --trace {} -o {} --config {} > {}".format(
        NEUTU_PATH, ORIGIN_PATH, LOC_TEST_PATH, LOC_CONFIG_PATH, LOG_PATH
    )
    try:
        os.system(REC_CMD)
    except:
        raise Exception("[Error: ] error executing reconstruction")

    res_tree = swc_node.SwcTree()
    gold_tree = swc_node.SwcTree()
    res_tree.load(os.path.join(TEST_PATH, test_name+".swc"))
    gold_tree.load(GOLD_PATH)

    if lock is not None:
        lock.acquire()
    try:
        main_score = g_metric_method(gold_tree, res_tree, g_metric_configs)
    finally:
        if lock is not None:
            lock.release()
    score = (main_score["recall"] + main_score["precision"])/2
    print("[Info: ] ssd loss = {}".format(score))

    return configs, -score


def main():
    global g_metric_configs
    global g_metric_method
    global g_rcn_config
    g_metric_method = ssd_metric.ssd_metric
    g_metric_configs = read_json.read_json(METRIC_CONFIG_PATH)
    g_rcn_config = read_json.read_json(os.path.join(CONFIG_PATH, "test.json"))

    # optimize with SA
    # configs here is the config of the reconstruction
    configs = (0.3, 0.3, 0.35, 0.5)
    start = time.time()
    sa_fast = SAFast(func=SA_optimize,
                     x0=configs, T_max=0.01, T_min=1e-5, q=0.96, L=20, max_stay_counter=50, upper=1, lower=0)
    best_configs, best_value = sa_fast.run()
    print("[Info: ]best configs:\n"
          "        origin minimalScoreAuto = {}\n"
          "        minimalScoreManual = {}\n"
          "        minimalScoreSeed = {}\n"
          "        minimalScore2d = {}\n"
          "        best value = {}\n"
          "        time = {}\n" .format(
        best_configs[0], best_configs[1], best_configs[2], best_configs[3], best_value, time.time() - start
    ))
    g_rcn_config["trace"]["default"]["minimalScoreAuto"] = best_configs[0]
    g_rcn_config["trace"]["default"]["minimalScoreManual"] = best_configs[1]
    g_rcn_config["trace"]["default"]["minimalScoreSeed"] = best_configs[2]
    g_rcn_config["trace"]["default"]["minimalScore2d"] = best_configs[3]
    read_json.save_json(os.path.join(CONFIG_PATH, "best_x_{}.json".format(time.time())), g_rcn_config)
    # plot the result.
    plt.plot(pd.DataFrame(sa_fast.best_y_history).cummin(axis=0))
    plt.xlabel("iterations")
    plt.ylabel("score(opposite value)")
    plt.show()
    return 0


if __name__ == "__main__":
    main()

    # g_metric_method = ssd_metric.ssd_metric
    # g_metric_configs = read_json.read_json(METRIC_CONFIG_PATH)
    # g_rcn_config = read_json.read_json(os.path.join(CONFIG_PATH, "test3best.json"))
    #
    # SA_optimize(test_name="test3best")
