import os
import csv
import unittest
import time
import numpy as np
import multiprocessing as mp

from pyneval.metric.utils.klib import TiffFile
from pyneval.io import read_json
from pyneval.model import swc_node
from pyneval.metric import length_metric as lm
from pyneval.metric import diadem_metric as dm
from pyneval.metric import branch_leaf_metric as bm
from pyneval.metric import link_metric as lkm
from pyneval.metric import ssd_metric as ssdm
from pyneval.metric import volume_metric as vm

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
            try:
                if len(row) == 0:
                    continue
                if fg == 0:
                    avgs.append(list(map(float, row)))
                else:
                    stds.append(list(map(float, row)))
                fg ^= 1
            except:
                pass

    linechar_visual(
        avgs=avgs,
        stds=stds,
        output_dir=pic_path,
        file_name=os.path.basename(csv_path)[:-4] + '.svg',
        lables=label_list,
    )


def csv_to_pic(csv_path, pic_path, label_list=[]):
    for csv_file in os.listdir(csv_path):
        csv_to_pic_single(os.path.join(csv_path, csv_file), pic_path, label_list=label_list)


def res_to_csv(swc_file, swc_res, csv_path=None, concern_list=[]):
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
        with open(os.path.join(csv_path, swc_file+".csv"), 'w') as f:
            c_writer = csv.writer(f)
            for i in range(len(avgs)):
                c_writer.writerow(avgs[i])
                c_writer.writerow(stds[i])


# def test_template(func_method, func_args, gold_dir, test_dir, generate_method="volume_move"):
#     '''
#     This function calculate the metric result on all test data of one metric method
#     '''
#     sys.setrecursionlimit(1000000)
#     # res
#     metric_results = {}
#     # choose the modified way: "move" or "delete"
#     # test_method_dir sample: test_dir/move
#     test_method_dir = os.path.join(test_dir, generate_method)
#
#     for swc_data in os.listdir(test_method_dir):
#         # swc_dir sample: test_dir/volume_move/a
#         test_method_swc_dir = os.path.join(test_method_dir, swc_data)
#
#         gold_tree = swc_node.SwcTree()
#         gold_tree.load(os.path.join(gold_dir, swc_data+".swc"))
#
#         swc_res = []
#         for per in os.listdir(test_method_swc_dir):
#             # final_dir sample: test_dir/volume_move/a/10
#             final_dir = os.path.join(test_method_swc_dir, per)
#
#             results = []
#             pool = mp.Pool(processes=CPU_CORE_NUM)
#             for file in os.listdir(final_dir):
#                 test_tree = swc_node.SwcTree()
#                 test_tree.load(os.path.join(final_dir, file))
#                 results.append(
#                     pool.apply_async(func_method, args=tuple([test_tree, gold_tree])+func_args)
#                 )
#                 # results.append(func_method(gold_tree, test_tree,func_args[0], func_args[1]))
#             pool.close()
#             pool.join()
#             clean_result = []
#             for result in results:
#                 clean_result.append(list(result.get()))
#             swc_res.append(clean_result)
#             print("{}----{}".format(swc_data, per))
#         metric_results[swc_data] = swc_res
#     return metric_results


def single_test(test_metric, metric_args, gold_file, test_file_path):
    '''
    This function calculates the metric result between 10% and 100% change when metric method and data is chosen.
    Args:
        test_metric(func): function name of metric to test:
        metric_args(tuple): arguments of tested metric
        file(str): tested file name
        gold_dir(str): path of gold file
        test_file_path(str): basic path of test file
        Example:
            test_file_path:  test_dir/generate_method/file
    Result:
        result(list):
            [
                [average_arg1_10%, average_arg1_20%,..., average_arg1_100%],
                [std_arg1_10%, std_arg1_20%,..., std_arg1_100%],
                [average_arg2_10%, average_arg2_20%,..., average_arg2_100%],
                [std_arg2_10%, std_arg2_20%,..., std_arg2_100%],
                ...
            ]
    '''
    gold_tree = swc_node.SwcTree()
    gold_tree.load(gold_file)

    swc_res = []
    for percentage in os.listdir(test_file_path):
        print("{}---{}".format(gold_file, percentage))
        # final_dir sample: test_dir/volume_move/a/10
        final_dir = os.path.join(test_file_path, percentage)

        per_res = []
        pool = mp.Pool(processes=CPU_CORE_NUM)
        for file in os.listdir(final_dir):
            test_tree = swc_node.SwcTree()
            test_tree.load(os.path.join(final_dir, file))
            per_res.append(
                pool.apply_async(test_metric, args=tuple([gold_tree, test_tree])+metric_args)
            )
            # results.append(func_method(gold_tree, test_tree,func_args[0], func_args[1]))
        pool.close()
        pool.join()
        result_values = []
        for result in per_res:
            result_values.append(list(result.get().values()))
        swc_res.append(result_values)
    return swc_res


def batch_test(test_datas, gold_dir, test_dir, method):
    metric_names = ["ssd_metric", "length_metric", "diadem_metric", "branch_metric", "link_metric"]
    metrics = {
        "ssd_metric": ssdm.ssd_metric,
        "length_metric": lm.length_metric,
        "diadem_metric": dm.diadem_metric,
        "branch_metric": bm.branch_leaf_metric,
        "link_metric": lkm.link_metric}
    configs = {
        "ssd_metric": read_json.read_json("..\\..\\config\\ssd_metric.json"),
        "length_metric": read_json.read_json("..\\..\\config\\length_metric.json"),
        "diadem_metric": read_json.read_json("..\\..\\config\\diadem_metric.json"),
        "branch_metric": read_json.read_json("..\\..\\config\\branch_metric.json"),
        "link_metric": read_json.read_json("..\\..\\config\\link_metric.json")}
    labels = {
        "ssd_metric": ["ssd_score", "recall", "precision"],
        "length_metric": ["recall", "precision"],
        "diadem_metric": ["final_score"],
        "branch_metric": ["true_positive_number", "false_negative_num", "false_positive_num", "matched_mean_distance"],
        "link_metric": ["edge_loss", "tree_dis_loss"]
    }
    metric_result = {}
    test_method_dir = os.path.join(test_dir, method)
    for metric in metric_names:
        for data in test_datas:
            swc_res = single_test(test_metric=metrics[metric],
                                  metric_args=(configs[metric], ),
                                  gold_file=os.path.join(gold_dir, data+".swc"),
                                  test_file_path=os.path.join(test_method_dir, data))
            metric_result[metric+"_"+data+"_"+method] = swc_res
            res_to_csv(swc_file=data,
                       swc_res=swc_res,
                       csv_path=os.path.join(out_dir, "csv_dir"))


if __name__=='__main__':
    sys.setrecursionlimit(10000000)
    metric_names = ["ssd_metric", "length_metric", "diadem_metric", "branch_metric", "link_metric"]
    labels = {
        "ssd_metric": ["ssd_score", "recall", "precision"],
        "length_metric": ["recall", "precision"],
        "diadem_metric": ["final_score"],
        "branch_metric": ["true_positive_number", "false_negative_num", "false_positive_num", "matched_mean_distance"],
        "link_metric": ["edge_loss", "tree_dis_loss"]
    }

    gold_dir = "../../data/example_selected"
    test_dir = "../../output/random_data"
    out_dir = "../../output/"
    config = read_json.read_json("..\\..\\config\\ssd_metric.json")
    method = "diadem"
    # batch_test()
    # res = single_test(test_metric=ssdm.ssd_metric,
    #                   metric_args=(config, ),
    #                   test_file_path="E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\output\\random_data\move\\a",
    #                   gold_file="E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\data\example_selected\\a.swc")
    # res_to_csv("a_ssd", res,
    #            csv_path="E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\output\csv_dir",
    #            concern_list=[0,1,2])
    for metric in metric_names:
        csv_to_pic(csv_path=os.path.join("E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\output\csv_dir", metric[:-7]),
                   pic_path="E:\\00_project\\00_neural_reconstruction\\01_project\PyNeval\output\pic_dir",
                   label_list=labels[metric])