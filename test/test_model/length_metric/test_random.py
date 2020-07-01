import os
import unittest, time
import numpy as np
import multiprocessing as mp

from pyneval.io.save_swc import swc_save
from pyneval.io.read_json import read_json
from pyneval.model.swc_node import SwcNode, SwcTree
from pyneval.metric.length_metric import length_metric
from pyneval.metric.diadem_metric import diadem_metric
from test.data_builder.dbuilder import build_random, delete_random
import sys

CPU_CORE_NUM = 11

def lm_move_percentage_test(gold_tree, move_percentage, move_num, move_range, move_tendency):
    avg_recalls = []
    avg_precisions = []

    for it in range(11):
        recalls = []
        precitions = []
        jter = 10
        for jt in range(jter):
            test_tree = build_random(swc_tree=gold_tree,
                                     move_percentage=it * 0.1,
                                     move_num=None,
                                     move_range=move_range,
                                     tendency=move_tendency)

            recall, precision, ver = length_metric(gold_swc_tree=gold_tree,
                                                   test_swc_tree=test_tree,
                                                   abs_dir="",
                                                   config=read_json("..\..\..\config\length_metric.json"))

            recalls.append(recall)
            precitions.append(precision)
        recalls = np.array(recalls)
        precitions = np.array(precitions)
        avg_recalls.append((recalls.sum()/jter, recalls.std()))
        avg_precisions.append((precitions.sum()/jter, precitions.std()))

    return avg_recalls, avg_precisions


def lm_move_range_test(gold_tree, move_percentage, move_num, move_tendency):
    avg_recalls = []
    avg_precisions = []
    config = read_json("..\..\..\config\length_metric.json")
    for it in range(11):
        recalls = []
        precitions = []
        jter = 10

        pool = mp.Pool(processes=12)
        test_trees = []
        for jt in range(jter):
            test_trees.append(
                pool.apply_async(build_random, args=(gold_tree, move_percentage, move_num, it * 1.0, move_tendency))
            )

        pool.close()
        pool.join()

        pool_metric = mp.Pool(processes=12)
        res_list = []
        for jt in range(jter):
            test_tree = SwcTree()
            test_tree.load_list(test_trees[jt].get().split("\n"))
            res_list.append(
                pool_metric.apply_async(length_metric, args=(gold_tree, test_tree, "", config))
            )

        pool_metric.close()
        pool_metric.join()
        for item in res_list:
            recalls.append(item.get()[0])
            precitions.append(item.get()[1])

        recalls = np.array(recalls)
        precitions = np.array(precitions)
        avg_recalls.append((recalls.sum()/jter, recalls.std()))
        avg_precisions.append((precitions.sum()/jter, precitions.std()))

    return avg_recalls, avg_precisions


def lm_delete_percentage_test(gold_tree, move_percentage, move_num):
    avg_recalls = []
    avg_precisions = []

    gold_tree_str = gold_tree.to_str_list().split("\n")
    config = read_json("..\..\..\config\length_metric.json")
    for it in range(11):
        recalls = []
        precitions = []
        jter = 10

        pool = mp.Pool(processes=12)
        test_trees = []
        for jt in range(jter):
            gold_tree = SwcTree()
            gold_tree.load_list(gold_tree_str)

            test_trees.append(
                pool.apply_async(delete_random, args=(gold_tree, it*0.1, move_num, ))
            )

        pool.close()
        pool.join()

        pool_metric = mp.Pool(processes=12)
        res_list = []
        for jt in range(jter):
            test_tree = SwcTree()
            gold_tree = SwcTree()
            gold_tree.load_list(gold_tree_str)
            test_tree.load_list(test_trees[jt].get().split("\n"))
            res_list.append(
                pool_metric.apply_async(length_metric, args=(gold_tree, test_tree, "", config))
            )

        pool_metric.close()
        pool_metric.join()
        print("{} down".format(it))
        for item in res_list:
            recalls.append(item.get()[0])
            precitions.append(item.get()[1])

        recalls = np.array(recalls)
        precitions = np.array(precitions)
        avg_recalls.append((recalls.sum()/jter, recalls.std()))
        avg_precisions.append((precitions.sum()/jter, precitions.std()))

    return avg_recalls, avg_precisions


def dm_test(gold_tree, test_trees, move_percentage, move_num):
    sys.setrecursionlimit(1000000)
    avg_recalls, avg_precisions= [], []
    config = read_json("..\..\..\config\diadem_metric.json")
    gold_tree_str = gold_tree.to_str_list().split("\n")

    recalls, precitions, jter = [], [], 200
    # get recalls&precisions
    pool_metric = mp.Pool(processes=CPU_CORE_NUM)
    res_list = []
    for jt in range(jter):
        gold_tree = SwcTree()
        gold_tree.load_list(gold_tree_str)
        print("test: {}".format(jt))
        res_list.append(
            pool_metric.apply_async(diadem_metric, args=(gold_tree, test_trees[jt], config, False, ))
        )
    pool_metric.close()
    pool_metric.join()
    # manage data to return
    for item in res_list:
        print(item.get())
        recalls.append(item.get())

    recalls = np.array(recalls)
    return tuple([recalls.sum() / jter, recalls.std()])


def data_random_delete(gold_tree, file_path_out):
    for it in range(15):
        jter = 1000
        pool = mp.Pool(processes=CPU_CORE_NUM)

        # get test trees
        test_trees = []
        for jt in range(jter):
            test_trees.append(
                pool.apply_async(delete_random, args=(gold_tree, None, it * 1.0, ))
            )
        pool.close()
        pool.join()

        pool_metric = mp.Pool(processes=CPU_CORE_NUM)
        for jt in range(jter):
            test_tree = SwcTree()
            test_tree.load_list(test_trees[jt].get().split("\n"))
            if not os.path.exists(os.path.join(file_path_out, '{}_dm_mv'.format(it))):
                os.mkdir(os.path.join(file_path_out, '{}_dm_mv'.format(it)))
            pool_metric.apply_async(swc_save, args=(test_tree,
                                                    os.path.join(os.path.join(file_path_out,
                                                                              '{}_dm_mv'.format(it)),
                                                                              "{}_{}_dm_mv.txt".format(it, jt))))
        pool_metric.close()
        pool_metric.join()


def data_random_move(gold_tree, file_path_out):
    for it in range(3,4):
        jter = 100
        pool = mp.Pool(processes=CPU_CORE_NUM)

        # get test trees
        test_trees = []
        for jt in range(jter):
            test_trees.append(
                pool.apply_async(build_random, args=(gold_tree, it*0.05, None, 1.0, (1, 1, 1), ))
            )
        pool.close()
        pool.join()

        pool_metric = mp.Pool(processes=CPU_CORE_NUM)
        for jt in range(jter):
            if not os.path.exists(os.path.join(file_path_out, '{}_dm_mv'.format(it))):
                os.mkdir(os.path.join(file_path_out, '{}_dm_mv'.format(it)))
            test_tree = SwcTree()
            test_tree.load_list(test_trees[jt].get().split("\n"))
            pool_metric.apply_async(swc_save, args=(test_tree,
                                                    os.path.join(os.path.join(file_path_out, '{}_dm_mv'.format(it)),
                                                                                             "{}_{}_dm_mv.txt".format(it, jt))))

        pool_metric.close()
        pool_metric.join()


def test_io(func_method, file_path_in, file_path_out, test_fold, file_name):
    sys.setrecursionlimit(1000000)
    files = os.listdir(file_path_in)
    avg_recalls, avg_precisions = [], []
    for file in files:
        print("filename = {}".format(file))
        gold_tree = SwcTree()
        gold_tree.load(os.path.join(file_path_in, file))
        test_path_in = os.path.join(file_path_in, test_fold)
        for it in range(11):
            test_path_tmp = os.path.join(test_path_in, '{}_dm_mv'.format(it))
            test_trees = []

            pool = mp.Pool(processes=CPU_CORE_NUM)
            for test in os.listdir(test_path_tmp):
                test_tree = SwcTree()
                test_tree.load(os.path.join(test_path_tmp, test))
                test_trees.append(test_tree)

            print("test start:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            avg_recall, avg_precision = func_method(gold_tree=gold_tree,
                                                    test_trees=test_trees,
                                                    move_percentage=None,
                                                    move_num=None)
            avg_precisions.append(avg_precisions)
            avg_recalls.append(avg_recall)

        with open(os.path.join(file_path_out, file_name), 'a') as f:
            for item in avg_recalls:
                f.write("{} ".format(str(item[0])))
            f.write("\n")
            for item in avg_recalls:
                f.write("{} ".format(str(item[1])))
            f.write("\n")
        with open(os.path.join(file_path_out, file_name), 'a') as f:
            for item in avg_precisions:
                f.write("{} ".format(str(item[0])))
            f.write("\n")
            for item in avg_precisions:
                f.write("{} ".format(str(item[1])))
            f.write("\n")
        print("test end:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__=='__main__':
    sys.setrecursionlimit(1000000)
    file_path_in = "D:\gitProject\mine\PyNeval\\test\data_example\gold\\random_test_data\\diadem_data"
    file_path_out = "D:\\gitProject\\mine\\PyNeval\\test\\test_model\\visualize\\input_data"

    # test_io(lm_delete_percentage_test, file_path_in, file_path_out, 'tmp_out.txt')
    # test_io(dm_delete_num_test, file_path_in, file_path_out, 'std1_delete_random', 'dm_delete_percentage_out.txt')
    # test_io(dm_test, file_path_in, file_path_out, 'std1_delete_random_1000', 'dm_mv_percentage_out_1000.txt')

    # data prepare
    # start = time.time()
    # gold_tree = SwcTree()
    # gold_tree.load("D:\gitProject\mine\PyNeval\\test\data_example\gold\\random_test_data\diadem_data\diadem_std1.swc")
    # file_data_path_out = "D:\gitProject\mine\PyNeval\\test\data_example\gold\\random_test_data\diadem_data\std1_delete_random_1000"
    # data_random_delete(gold_tree, file_data_path_out)
    # print("time = {}".format(time.time() - start))

    scores = []
    with open("D:\gitProject\mine\PyNeval\\test\\test_model\\visualize\input_data\dm_1000.txt") as f:
        lines = f.readlines()
    tot_str = "".join(lines)
    print(tot_str.split('\n'))
    nums = list(map(float, tot_str.split('\n')))
    for i in range(11):
        scores.append(nums[i*200:(i+1)*200])
    with open("D:\gitProject\mine\PyNeval\\test\\test_model\\visualize\input_data\dm_delete_percentage_out_1000.txt", 'a') as f:
        for score in scores:
            f.write("{} ".format(np.array(score).sum() / 200))
        f.write("\n")
        for score in scores:
            f.write("{} ".format(np.array(score).std()))
        f.write("\n")