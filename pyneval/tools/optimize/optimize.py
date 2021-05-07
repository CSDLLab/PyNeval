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

# def fake_gaussian(mean=[0.0, 0.0], cov=[[0.0, 1.0], [1.0, 0.0]], pos=(0,0)):
#     rv = st.multivariate_normal(mean=[1.5, -1], cov=[[0.5, 0],[0, 0.5]])
#     rv2 = st.multivariate_normal(mean=[-0.1, 0.5], cov=[[1, 0],[0, 1]])
#     x = np.empty(shape=(1, 1, 2))
#     x[0,0,0] = pos[0]
#     x[0,0,1] = pos[1]
#     return rv.pdf(x) + rv2.pdf(x)


# def naive_optimize(gold_tree, rcn_configs, current_config, metric_method, metric_configs):
#     """
#     A naive optimization, test every combination of test parameters
#     recursive parameter searching is used for traversing all the combinations.
#     """
#     clen = len(current_config)
#     if clen == len(rcn_configs):
#         # metric and get results
#         # # check the value of configs
#         # res = fake_gaussian(pos=configs)
#         rec_config = read_json.read_json(json_file_path=CONFIG_PATH)
#         current_config[0] = max(current_config[0], 0)
#         current_config[1] = max(current_config[1], 0)
#         print("[Info: ] minimalScoreAuto = {} minimalScoreSeed = {}".format(
#             current_config[0], current_config[1])
#         )
#         rec_config["trace"]["default"]["minimalScoreAuto"] = rcn_configs[0]
#         rec_config["trace"]["default"]["minimalScoreSeed"] = rcn_configs[1]
#
#         # save new configs
#         read_json.save_json(json_file_path=CONFIG_PATH, data=rec_config)
#         REC_CMD = "{} --command --trace {} -o {} --config {}".format(
#             NEUTU_PATH, ORIGIN_PATH, TEST_PATH, CONFIG_PATH
#         )
#         print(REC_CMD)
#         try:
#             print("[Info: ] start tracing")
#             os.system(REC_CMD)
#             print("[Info: ] end tracing")
#         except:
#             raise Exception("[Error: ] error executing reconstruction")
#
#         res_tree = swc_node.SwcTree()
#         gold_tree = swc_node.SwcTree()
#         res_tree.load(TEST_PATH)
#         gold_tree.load(GOLD_PATH)
#
#         main_score = g_metric_method(gold_tree, res_tree, g_metric_configs)
#         # main_score = fake_gaussian(mean=[0.5, -0.3], cov=[[1, 0],[0, 1]], pos=current_config)
#         global g_score
#         if main_score > g_score:
#             g_score = main_score
#             print("max_score = {}, current_score = {}, x = {}, y = {}".format(
#                 g_score, main_score, current_config[0], current_config[1])
#             )
#         return None
#
#     for item in rcn_configs[clen]:
#         current_config.append(item)
#         naive_optimize(gold_tree=gold_tree,
#                        rcn_method=rcn_method,
#                        rcn_configs=rcn_configs,
#                        current_config=current_config,
#                        metric_method=metric_method,
#                        metric_configs=metric_configs)
#         current_config.pop()
#     return None


# def naive_main():
#     global g_metric_configs
#     global g_metric_method
#     g_metric_method = ssd_metric.ssd_metric
#     g_metric_configs = read_json.read_json(METRIC_CONFIG_PATH)
#
#     z = np.zeros(shape=(50, 50))
#     for i in range(50):
#         for j in range(50):
#             rec_config = read_json.read_json(json_file_path=CONFIG_PATH)
#             rec_config["trace"]["default"]["minimalScoreAuto"] = 0.02 * i
#             rec_config["trace"]["default"]["minimalScoreSeed"] = 0.02 * j
#             read_json.save_json(json_file_path=CONFIG_PATH, data=rec_config)
#             REC_CMD = "{} --command --trace {} -o {} --config {}".format(
#                 NEUTU_PATH, ORIGIN_PATH, TEST_PATH, CONFIG_PATH
#             )
#             print(REC_CMD)
#             try:
#                 print("[Info: ] start tracing")
#                 os.system(REC_CMD)
#                 print("[Info: ] end tracing")
#             except:
#                 raise Exception("[Error: ] error executing reconstruction")
#
#             res_tree = swc_node.SwcTree()
#             gold_tree = swc_node.SwcTree()
#             res_tree.load(TEST_PATH)
#             gold_tree.load(GOLD_PATH)
#
#             main_score = g_metric_method(gold_tree, res_tree, g_metric_configs)
#             print("[Info: ] call = {} minimalScoreAuto = {} minimalScoreSeed = {}".format(
#                 main_score["recall"], 0.02 * i, 0.02 * j
#             ))
#             z[i][j] = main_score["recall"]
#
#     # print(z)
#     x = np.linspace(0, 0.48, 50)
#     y = np.linspace(0, 0.48, 50)
#     X, Y = np.meshgrid(x, y)
#
#     fig = plt.figure()
#     # 创建一个三维坐标轴
#     ax = plt.axes(projection='3d')
#     ax.contour3D(X, Y, z, 50, cmap='binary')
#     ax.set_xlabel('x')
#     ax.set_ylabel('y')
#     ax.set_zlabel('z')
#     ax.plot_surface(X, Y, z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
#     ax.set_title('surface')
#     plt.show()
#     print(X.shape)


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
                     x0=configs, T_max=0.01, T_min=1e-5, q=0.96, L=20, max_stay_counter=30, upper=1, lower=0)
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
