import os
import copy
import time
import matplotlib.pyplot as plt
import pandas as pd
import importlib

from pyneval.tools.optimize.SA import SAFast
from pyneval.metric import ssd_metric
from pyneval.metric.utils import config_utils
from pyneval.model import swc_node
from pyneval.io import read_json
from pyneval.metric.utils import metric_manager
    

def SA_optimize(gold_tree=None, metric_method=None, config=None, 
                metric_config=None, optimize_config=None,
                test_name=None, lock=None):
    # fullfill cmd 
    CURRENT_TEST_PATH = os.path.join(optimize_config["TRACE_CMD"]["TEST_SWC_DIR"], test_name+"_test.swc")
    REC_CMD = optimize_config["TRACE_CMD"]["CMD"].format(CURRENT_TEST_PATH, config)
    # run cmd
    try:
        os.system(REC_CMD)
    except:
        raise Exception("[Error: ] error executing reconstruction")
    # run metric
    res_tree = swc_node.SwcTree()
    res_tree.load(CURRENT_TEST_PATH)

    if lock is not None:
        lock.acquire()
    try:
        main_score, _, _ = metric_method(gold_tree, res_tree, metric_config)
    finally:
        if lock is not None:
            lock.release()
    # avg
    # score = (main_score["recall"] + main_score["precision"])/2
    # f1
    try:
        score = 2*main_score["recall"]*main_score["precision"]/(main_score["recall"] + main_score["precision"])
    except:
        score = 0
    print("[Info: ] ssd loss = {}".format(score))

    return config, -score



def check_save(gold_tree, metric_method, metric_config, optimize_config, best_name, best_configs):
    # fullfill cmd 
    BEST_TEST_PATH = os.path.join(optimize_config["TRACE_CMD"]["TEST_SWC_DIR"], best_name+"_best.swc")
    REC_CMD = optimize_config["TRACE_CMD"]["CMD"].format(BEST_TEST_PATH, best_configs)
    # run cmd
    try:
        os.system(REC_CMD)
    except:
        raise Exception("[Error: ] error executing reconstruction")
    # run metric
    res_tree = swc_node.SwcTree()
    res_tree.load(BEST_TEST_PATH)

    main_score, _, _ = metric_method(gold_tree, res_tree, metric_config)
    try:
        score = 2*main_score["recall"]*main_score["precision"]/(main_score["recall"] + main_score["precision"])
    except:
        score = 0
    for key in main_score:
        print("{}:{}".format(key, main_score[key]))
    print("f1 score:{}".format(score))


def optimize(gold_swc_tree, test_swc_paths, optimize_config, metric_config, metric_method):
    start_timestep = time.time()
    # set test tiff path
    optimize_config["TRACE_CMD"]["ORIGIN_TIFF_PATH"] = test_swc_paths[0]
    # put normal parameters into cmd, except for output swc
    optimize_config["TRACE_CMD"]["CMD"] = optimize_config["TRACE_CMD"]["CMD"].format(
        optimize_config["TRACE_CMD"]["TRACE_TOOL_PATH"], 
        optimize_config["TRACE_CMD"]["ORIGIN_TIFF_PATH"], 
        "{0}"
    )
    # add target parameters into cmd 
    it = 0
    for key in optimize_config["TRACE_CMD"]["INITIAL_PARAS"]:
        optimize_config["TRACE_CMD"]["CMD"] += (" " + key + " {1[" + str(it) + "]}")
        it+=1
    # initialize and run SA model 
    sa_fast = SAFast(func=SA_optimize, gold_swc_tree=gold_swc_tree, metric_method=metric_method, 
                     metric_config=metric_config, optimize_config=optimize_config, 
                     x0=list(optimize_config["TRACE_CMD"]["INITIAL_PARAS"].values()), upper=1, lower=0)
    best_configs, best_value = sa_fast.run(gold_swc_tree=gold_swc_tree, metric_method=metric_method, 
                                           metric_config=metric_config, optimize_config=optimize_config)
    # output the best parameters
    i=0
    print("[Info: ]best configs:")
    for key in optimize_config["TRACE_CMD"]["INITIAL_PARAS"]:
        print("best {} = {}".format(key, best_configs[i]))
        i+=1
    print(
        "best value = {}\n"
        "time = {}\n" .format(best_value, time.time() - start_timestep)
    )
    # get and save best reconstruct swc
    print("[Info: ]Exam test score with best configs: ")
    best_name = os.path.basename(optimize_config["TRACE_CMD"]["ORIGIN_TIFF_PATH"])[:-4]
    check_save(gold_tree=gold_swc_tree, metric_method=metric_method, 
               metric_config=metric_config, optimize_config=optimize_config, 
               best_name=best_name, best_configs=best_configs)

    # plot the result.
    plt.plot(pd.DataFrame(sa_fast.best_y_history).cummin(axis=0))
    plt.xlabel("iterations")
    plt.ylabel("score(opposite value)")
    plt.show()
    return 0

if __name__ == "__main__":
    pass

# pyneval --gold data/optimation/test1/test1_gold.swc --test data/optimation/test1/test1_test.tif --metric ssd --optimize pyneval/tools/optimize/opt_config.json
