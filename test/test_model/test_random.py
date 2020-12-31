import os
import csv
import unittest, time
import numpy as np
import multiprocessing as mp

from pyneval.metric.utils.klib.TiffFile import imread
from pyneval.io.save_swc import swc_save
from pyneval.io.read_json import read_json
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.metric.length_metric import length_metric
from pyneval.metric.diadem_metric import diadem_metric
from pyneval.metric.branch_leaf_metric import branch_leaf_metric
from pyneval.metric.link_metric import link_metric
from pyneval.metric.ssd_metric import ssd_metric
from pyneval.metric.volume_metric import volume_metric

from test.test_model.visualize.linechart_visual import linechar_visual

import sys

CPU_CORE_NUM = 12


def csv_to_pic_single(csv_path, pic_path, label_list=[]):
    stds, avgs = [], []
    if os.path.isdir(csv_path):
        return None
    fg = 0
    with open(csv_path, 'r', newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if len(row) == 0:
                continue
            if fg == 0:
                avgs.append(list(map(float, row)))
            else:
                stds.append(list(map(float, row)))
            fg ^= 1

    linechar_visual(
        avgs=avgs,
        stds=stds,
        output_dir=pic_path,
        file_name=csv_path[:-4] + '.png',
        lables=label_list
    )


def csv_to_pic(csv_path, pic_path, label_list=[]):
    for csv_file in os.listdir(csv_path):
        csv_to_pic_single(os.path.join(csv_path, csv_file), pic_path, label_list=label_list)


def res_to_csv(metric_results, method="", csv_path=None, pic_path=None, concern_list=[], label_list=[]):
    for swc_file in metric_results.keys():
        swc_res = metric_results[swc_file]
        avgs = []
        stds = []
        for i in range(len(concern_list)):
            avgs.append([])
            stds.append([])

        for raw_per_data in swc_res:
            np_raw_per_data = np.array(raw_per_data)
            avg = np_raw_per_data.mean(axis=0)
            std = np_raw_per_data.std(axis=0)
            for i in range(len(avgs)):
                avgs[i].append(avg[concern_list[i]])
                stds[i].append(std[concern_list[i]])

        if csv_path is not None:
            with open(os.path.join(csv_path, swc_file+method+".csv"), 'w') as f:
                c_writer = csv.writer(f)
                for i in range(len(avgs)):
                    c_writer.writerow(avgs[i])
                    c_writer.writerow(stds[i])

        # paint different features of a single swc on the same pic
        if pic_path is not None:
            linechar_visual(
                avgs=avgs,
                stds=stds,
                output_dir=pic_path,
                file_name=swc_file,
                lables=label_list
            )


def test_template(func_method, func_args, gold_dir, test_dir, generate_method="volume_move"):
    '''
    input: gold_file_in: path to randomly generated different
    output: average recall on different change rates
    '''
    sys.setrecursionlimit(1000000)
    # res
    metric_results = {}
    # choose "volume_move" or "delete"
    # gm_dir sample: test_dir/volume_move
    gm_dir = os.path.join(test_dir, generate_method)

    for swc_data in os.listdir(gm_dir):
        # swc_dir sample: test_dir/volume_move/a
        swc_dir = os.path.join(gm_dir, swc_data)
        gold_tree = None
        if generate_method == "volume_move":
            gold_tree = imread(os.path.join(gold_dir, swc_data+".tif"))
        else:
            gold_tree = SwcTree()
            gold_tree.load(os.path.join(gold_dir, swc_data+".swc"))

        swc_res = []
        for per in os.listdir(swc_dir):
            # final_dir sample: test_dir/volume_move/a/10
            final_dir = os.path.join(swc_dir, per)

            results = []
            pool = mp.Pool(processes=CPU_CORE_NUM)
            for file in os.listdir(final_dir):
                test_tree = SwcTree()
                test_tree.load(os.path.join(final_dir, file))
                results.append(
                    pool.apply_async(func_method, args=tuple([test_tree, gold_tree])+func_args)
                )
                # results.append(func_method(gold_tree, test_tree,func_args[0], func_args[1]))
            pool.close()
            pool.join()
            clean_result = []
            for result in results:
                clean_result.append(list(result.get()))
            swc_res.append(clean_result)
            print("{}----{}".format(swc_data, per))
        metric_results[swc_data] = swc_res
    return metric_results


if __name__=='__main__':
    sys.setrecursionlimit(10000000)

    gold_dir = "../../data/example_selected"
    test_dir = "../../output/random_data"
    out_dir = "../../output/"
    config = read_json("../../config/volume_metric.json")
    # length metric
    # metric_results = test_template(func_method=ssd_metric,
    #                                func_args=(config, ),
    #                                gold_dir=gold_dir,
    #                                test_dir=test_dir,
    #                                # generate_method="delete")
    #                                generate_method="volume_move")
    # metric_results = test_template(func_method=volume_metric,
    #                                func_args=(config, ),
    #                                gold_dir=gold_dir,
    #                                test_dir=test_dir,
    #                                # generate_method="delete")
    #                                generate_method="volume_move")
    # metric_results = test_template(func_method=branch_leaf_metric,
    #                                func_args=(config, ),
    #                                gold_dir=gold_dir,
    #                                test_dir=test_dir,
    #                                generate_method="link")
    # metric_results = test_template(func_method=link_metric,
    #                                func_args=(config, ),
    #                                gold_dir=gold_dir,
    #                                test_dir=test_dir,
    #                                generate_method="link")
    label_list_branch = ["true_positive_number", "false_negative_num", "false_positive_num", "matched_mean_distance"]
    label_list_link = ["edge_loss", "tree_dis_loss"]
    label_list_ssd = ["ssd_score", "recall", "precision"]
    label_list_length = ["recall", "precision"]
    label_list_diadem = ["final_score"]
    label_list_volume = ["recall"]
    method = "volume"

    # len_res_to_csv(metric_results,
    #                csv_path=os.path.join(out_dir, "csv_dir"),
    #                pic_path=None,
    #                method=method,
    #                concern_list=[0],
    #                label_list=label_list_volume)
    csv_to_pic_single(csv_path=os.path.join(out_dir, "csv_dir/gvolume.csv"),
                      pic_path=os.path.join(out_dir, "pic_dir"),
                      label_list=label_list_volume)

