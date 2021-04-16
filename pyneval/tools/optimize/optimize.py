from pyneval.io import read_json
from pyneval.metric import ssd_metric
from test.data_builder import dbuilder
from pyneval.model import swc_node
from scipy import stats as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np
from sko.SA import SABoltzmann
import pandas as pd

g_score = -1
g_gold_tree = None
g_tar_tree = None
g_rcn_method = None
g_metric_method = None
g_metric_configs = None


def fake_gaussian(mean=[0.0, 0.0], cov=[[0.0, 1.0], [1.0, 0.0]], pos=(0,0)):
    rv = st.multivariate_normal(mean=[1.5, -1], cov=[[0.5, 0],[0, 0.5]])
    rv2 = st.multivariate_normal(mean=[-0.1, 0.5], cov=[[1, 0],[0, 1]])
    x = np.empty(shape=(1, 1, 2))
    x[0,0,0] = pos[0]
    x[0,0,1] = pos[1]
    return rv.pdf(x) + rv2.pdf(x)


def fake_reconstruction(gold_tree,  rcn_config):
    res_tree = dbuilder.swc_random_move(swc_tree=gold_tree,
                                        move_percentage=rcn_config[0],
                                        move_range=rcn_config[1])
    return res_tree


def metric(gold_tree, test_tree, method, configs):
    return method(gold_tree, test_tree, configs)


def naive_optimize(gold_tree, rcn_method, rcn_configs, current_config, metric_method, metric_configs):
    """
    A naive optimization, test every combination of test parameters
    recursive parameter searching is used for traversing all the combinations.
    """
    clen = len(current_config)
    if clen == len(rcn_configs):
        # metric and get results
        # res_tree = fake_reconstruction(gold_tree=gold_tree, method=rcn_method, rcn_config=current_config)
        # main_score = metric(gold_tree=gold_tree, test_tree=res_tree, method=metric_method, configs=metric_configs)
        main_score = fake_gaussian(mean=[0.5, -0.3], cov=[[1, 0],[0, 1]], pos=current_config)
        global g_score
        if main_score > g_score:
            g_score = main_score
            print("max_score = {}, current_score = {}, x = {}, y = {}".format(
                g_score, main_score, current_config[0], current_config[1])
            )
        return None

    for item in rcn_configs[clen]:
        current_config.append(item)
        naive_optimize(gold_tree=gold_tree,
                       rcn_method=rcn_method,
                       rcn_configs=rcn_configs,
                       current_config=current_config,
                       metric_method=metric_method,
                       metric_configs=metric_configs)
        current_config.pop()
    return None


def SA_optimize(configs):
    global g_gold_tree
    global g_metric_method
    global g_metric_configs

    res = fake_gaussian(pos=configs)
    # print("res = {} x = {} y = {}".format(res, configs[0], configs[1]))
    res_tree = fake_reconstruction(gold_tree=g_gold_tree, rcn_config=configs)
    main_score = metric(gold_tree=g_tar_tree, test_tree=res_tree, method=g_metric_method, configs=g_metric_configs)
    print("res = {} x = {} y = {}".format(main_score["recall"], configs[0], configs[1]))
    return -main_score["recall"]


def run_opt(rcn_method, metric_method):
    global g_gold_tree
    global g_tar_tree
    global g_rcn_method
    global g_metric_method
    global g_metric_configs

    g_gold_tree = swc_node.SwcTree()
    g_tar_tree = swc_node.SwcTree()
    g_gold_tree.load("..\\..\\..\\data\\example_selected\\c.swc")
    g_tar_tree.load("..\\..\\..\\output\\random_data\move_r\c\\020\move_00.swc")
    # rcn_configs = read_json.read_json("..\\..\\..\\config\\fake_reconstruction_configs\\branch_metric.json")
    g_metric_configs = read_json.read_json("..\\..\\..\\config\\ssd_metric.json")
    g_metric_method = ssd_metric.ssd_metric
    # cfgs = []
    # for cfg_name in rcn_configs:
    #     cfg = rcn_configs[cfg_name]
    #     cfgs.append(np.linspace(cfg[0], cfg[1], cfg[2]))
    #
    # naive_optimize(gold_tree=gold_tree,
    #                rcn_method=rcn_method,
    #                rcn_configs=cfgs,
    #                current_config=[],
    #                metric_method=metric_method,
    #                metric_configs=metric_configs)
    configs = [0, 0]
    sa_boltzmann = SABoltzmann(func=SA_optimize,
                               x0=configs, T_max=0.1, T_min=1e-6, q=0.96, L=30, max_stay_counter=150)
    sa_boltzmann.run()
    plt.plot(pd.DataFrame(sa_boltzmann.best_y_history).cummin(axis=0))
    plt.xlabel("iterations")
    plt.ylabel("score(opposite value)")
    plt.show()


if __name__ == "__main__":
    # run_opt(fake_reconstruction, ssd_metric.ssd_metric)
    # print(np.round(g_score, 4))
    import os
    cmd = "pyneval --gold ..\\..\\..\\data\\test_data\geo_metric_data\gold_34_23_10.swc --test ..\\..\\..\\data\\test_data\geo_metric_data\\test_34_23_10.swc --metric branch_metric"
    # ans = os.system("chdir")
    ans = os.system(cmd)
    print(type(ans))