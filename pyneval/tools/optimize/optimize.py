import os

from pyneval.tools.optimize.SA import SAFast
from pyneval.metric import ssd_metric
from pyneval.model import swc_node
from pyneval.io import read_json
from scipy import stats as st

import copy
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

g_score = -1
g_gold_tree = None
g_tar_tree = None
g_rcn_method = None
g_rcn_config = None
g_metric_method = None
g_metric_configs = None

# Gold file and Test tif need to placed in ../../../data/optimation
# and named after FILE_ID_test.tif, FILE_ID_gold.swc
FILE_ID = "test1"
NEUTU_PATH = "neutu"
ORIGIN_PATH = "../../../data/optimation/{}/{}_test.tif".format(FILE_ID, FILE_ID)
GOLD_PATH = "../../../data/optimation/{}/{}_gold.swc".format(FILE_ID, FILE_ID)
METRIC_CONFIG_PATH = "../../../config/ssd_metric.json"
LOG_PATH = "../../../output/optimization/neutu_log.txt"
# specific test name is given in SA.py
TEST_PATH = "../../../data/optimation/output/"
CONFIG_PATH = "../../../config/fake_reconstruction_configs/"



def SA_optimize(configs=None, test_name=None, lock=None):
    global g_metric_method
    global g_metric_configs
    global g_rcn_config
    # identify specific TEST output path and CONFIG input PATH
    LOC_TEST_PATH = os.path.join(TEST_PATH, test_name+"_test.swc")
    rec_config = copy.deepcopy(g_rcn_config)

    if configs is not None:
        LOC_CONFIG_PATH = os.path.join(CONFIG_PATH, test_name+".json")
        rec_config["trace"]["default"]["minimalScoreAuto"] = configs[0]
        rec_config["trace"]["default"]["minimalScoreSeed"] = configs[1]

        read_json.save_json(LOC_CONFIG_PATH, rec_config)
    else:
        LOC_CONFIG_PATH = os.path.join(CONFIG_PATH, "best_x_{}.json".format(test_name))

    REC_CMD = "{} --command --trace {} -o {} --config {} > {}".format(
        NEUTU_PATH, ORIGIN_PATH, LOC_TEST_PATH, LOC_CONFIG_PATH, LOG_PATH
    )
    try:
        os.system(REC_CMD)
    except:
        raise Exception("[Error: ] error executing reconstruction")

    res_tree = swc_node.SwcTree()
    gold_tree = swc_node.SwcTree()
    res_tree.load(LOC_TEST_PATH)
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
    g_rcn_config = read_json.read_json(os.path.join(CONFIG_PATH, "default.json"))

    # optimize with SA
    # configs here is the config of the reconstruction
    configs = (0.3, 0.35)
    start = time.time()
    sa_fast = SAFast(func=SA_optimize,
                     x0=configs, T_max=0.01, T_min=1e-5, q=0.96, L=25, max_stay_counter=15, upper=1, lower=0)
    best_configs, best_value = sa_fast.run()
    print("[Info: ]best configs:\n"
          "        origin minimalScoreAuto = {}\n"
          "        minimalScoreSeed = {}\n"
          "        best value = {}\n"
          "        time = {}\n" .format(
        best_configs[0], best_configs[1], best_value, time.time() - start
    ))
    # save best json file
    g_rcn_config["trace"]["default"]["minimalScoreAuto"] = best_configs[0]
    g_rcn_config["trace"]["default"]["minimalScoreSeed"] = best_configs[1]
    read_json.save_json(os.path.join(CONFIG_PATH, "best_x_{}.json".format(FILE_ID)), g_rcn_config)
    # get and save best reconstruct swc
    print("[Info: ]Exam test score with best configs: ")
    cfg, score = SA_optimize(test_name = FILE_ID)
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
    # g_rcn_config = read_json.read_json(os.path.join(CONFIG_PATH, "6656_2304_22016.json"))
    
    # SA_optimize(test_name="6656_2816_22016")
