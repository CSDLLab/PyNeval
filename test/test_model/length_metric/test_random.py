import os
import csv
import unittest, time
import numpy as np
import multiprocessing as mp

from pyneval.io.save_swc import swc_save
from pyneval.io.read_json import read_json
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.metric.length_metric import length_metric
from pyneval.metric.diadem_metric import diadem_metric
from test.test_model.visualize.linechart_visual import linechar_visual

import sys

CPU_CORE_NUM = 12


def len_csv_to_pic(csv_path, pic_path):
    rows = []
    for csv_file in os.listdir(csv_path):
        if os.path.isdir(os.path.join(csv_path, csv_file)):
            continue
        with open(os.path.join(csv_path, csv_file), 'r', newline='') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if len(row) != 0:
                    rows.append(list(map(float, row)))
        linechar_visual(
            avgs=[rows[0], rows[2]],
            stds=[rows[1], rows[3]],
            output_dir=pic_path,
            file_name=csv_file[:-4]+'.png',
            lables=["recall", "precision"]
        )


def len_res_to_csv(metric_results, csv_path=None, pic_path=None):
    for swc_file in metric_results.keys():
        swc_res = metric_results[swc_file]
        recall_avgs = []
        recall_stds = []
        precision_avgs = []
        precision_stds = []
        for raw_per_data in swc_res:
            np_raw_per_data = np.array(raw_per_data)

            avg = np_raw_per_data.mean(axis=0)
            std = np_raw_per_data.std(axis=0)

            recall_avgs.append(avg[0])
            recall_stds.append(std[0])
            precision_avgs.append(avg[1])
            precision_stds.append(std[1])
        if csv_path is not None:
            with open(os.path.join(csv_path, swc_file+".csv"), 'w') as f:
                c_writer = csv.writer(f)
                c_writer.writerow(recall_avgs)
                c_writer.writerow(recall_stds)
                c_writer.writerow(precision_avgs)
                c_writer.writerow(precision_stds)
        # paint different features of a single swc on the same pic
        if pic_path is not None:
            linechar_visual(
                avgs=[recall_avgs, precision_avgs],
                stds=[recall_stds, precision_stds],
                output_dir=pic_path,
                file_name=swc_file,
                lables=["recall", "precision"]
            )


def test_template(func_method, func_args, gold_dir, test_dir, generate_method="move"):
    '''
    input: gold_file_in: path to randomly generated different
    output: average recall on different change rates
    '''
    sys.setrecursionlimit(1000000)
    # res
    metric_results = {}
    # choose "move" or "delete"
    # gm_dir sample: test_dir/move
    gm_dir = os.path.join(test_dir, generate_method)

    for swc_data in os.listdir(gm_dir):
        # swc_dir sample: test_dir/move/a
        swc_dir = os.path.join(gm_dir, swc_data)
        gold_tree = SwcTree()
        gold_tree.load(os.path.join(gold_dir, swc_data+".swc"))
        swc_res = []
        for per in os.listdir(swc_dir):
            # final_dir sample: test_dir/move/a/10
            final_dir = os.path.join(swc_dir, per)

            results = []
            pool = mp.Pool(processes=CPU_CORE_NUM)
            for file in os.listdir(final_dir):
                test_tree = SwcTree()
                test_tree.load(os.path.join(final_dir, file))
                results.append(
                    pool.apply_async(func_method, args=tuple([gold_tree, test_tree])+func_args)
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
    sys.setrecursionlimit(1000000)

    gold_dir = "../../../data/example_selected"
    test_dir = "../../../output/random_data"
    out_dir = "../../../output/"
    config = read_json("../../../config/length_metric.json")
    # length metric
    metric_results = test_template(func_method=length_metric,
                                   func_args=("D:\\02_project\\00_neural_tracing\\01_project\PyNeval", config),
                                   gold_dir=gold_dir,
                                   test_dir=test_dir,
                                   generate_method="delete")

    # metric_results = test_template(func_method=length_metric,
    #                                func_args=("D:\\02_project\\00_neural_tracing\\01_project\PyNeval", config),
    #                                gold_dir=gold_dir,
    #                                test_dir=test_dir,
    #                                generate_method="move")

    len_res_to_csv(metric_results,
                   csv_path=os.path.join(out_dir, "csv_dir"),
                   pic_path=None)
    len_csv_to_pic(csv_path=os.path.join(out_dir, "csv_dir"),
                   pic_path=os.path.join(out_dir, "pic_dir"))
