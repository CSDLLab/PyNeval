from pyneval.metric.utils.klib.TiffFile import imread
from pyneval.model.swc_node import SwcTree
from pyneval.io.save_swc import swc_save
from pyneval.tools.re_sample import up_sample_swc_tree
import queue
import math


def adjust_swc_tree(swc_tree, tiff_file, thres_intensity, max_step=4):
    swc_list = swc_tree.get_node_list()
    for node in swc_list:
        if node.is_virtual():
            continue
        new_center = cal_label(node=node, test_tiff=tiff_file,
                               thres_intensity=thres_intensity, max_step=max_step)
        if not new_center:
            print("{} {} {} ".format(
                node.get_x(), node.get_y(), node.get_z()
            ))
            print("[Warning: ] step too little")
        else:
            node.set_x(new_center[0])
            node.set_y(new_center[1])
            node.set_z(new_center[2])


def get_dis(tuple_1, tuple_2):
    dx = tuple_1[0] - tuple_2[0]
    dy = tuple_1[1] - tuple_2[1]
    dz = tuple_1[2] - tuple_2[2]
    return math.sqrt(dx**2 + dy**2 + dz**2)


def cal_label(node, test_tiff, thres_intensity, max_step=0):
    que = queue.Queue()
    center = [round(node.get_x()), round(node.get_y()), round(node.get_z())]
    que.put(tuple([center, 0]))
    vis = set()
    vis.add(tuple(center))

    stp = [
        [1, 0, 0], [0, 1, 0], [0, 0, 1],
        [-1, 0, 0], [0, -1, 0], [0, 0, -1]
    ]

    while not que.empty():
        cur = que.get()
        cur_loc = cur[0]
        cur_step = cur[1]
        if cur_step > max_step:
            continue

        if 0 <= round(cur_loc[0]) < test_tiff.shape[2] and\
           0 <= round(cur_loc[1]) < test_tiff.shape[1] and\
           0 <= round(cur_loc[2]) < test_tiff.shape[0] and\
           test_tiff[round(cur_loc[2])][round(cur_loc[1])][round(cur_loc[0])] >= thres_intensity:
            return tuple([round(cur_loc[0]), round(cur_loc[1]), round(cur_loc[2])])

        for i in range(6):
            dx = cur_loc[0] + stp[i][0]
            dy = cur_loc[1] + stp[i][1]
            dz = cur_loc[2] + stp[i][2]
            new_pos = tuple([dx, dy, dz])
            if new_pos not in vis:
                vis.add(tuple([new_pos, cur_step + 1]))
                que.put(tuple([new_pos, cur_step + 1]))
    return False


def cal_volume_recall(test_tiff, gold_swc, thres_intensity):
    swc_node_list = gold_swc.get_node_list()
    tot_front, tot_back = 0, 0

    for node in swc_node_list:
        if node.is_virtual():
            continue
        if (len(node.children) == 0 or node.parent.is_virtual()) and\
                cal_label(node, test_tiff, thres_intensity, 0) is not False:
            tot_front += 1
        elif cal_label(node, test_tiff, thres_intensity, 1) is not False:
            tot_front += 1
        else:
            print("[Info: ] fail: {} {} {} {} {}".format(
                node.get_id(), round(node.get_x()), round(node.get_y()), round(node.get_z()),
                test_tiff[round(node.get_z())][round(node.get_y())][round(node.get_x())]
            ))
        tot_back += 1
    print(tot_front, tot_back)
    return tot_front/tot_back


def volume_metric(swc_gold, tiff_test, config=None):
    thres_length = config['thres_length']
    thres_intensity = config['thres_intensity']
    densed_swc_tree = up_sample_swc_tree(swc_tree=swc_gold, thres_length=thres_length)
    recall = cal_volume_recall(tiff_test, densed_swc_tree, thres_intensity)
    return recall


if __name__ == "__main__":
    swc_path = "D:\gitProject\mine\PyNeval\output\\volume_metric_test\\2_18_test.swc"
    tiff_path = "D:\gitProject\mine\PyNeval\\test\data_example\\test\\vol_metric\\6656_2304_22016_label.tif"
    test_tiff = imread(tiff_path)

    swc_tree = SwcTree()
    swc_tree.load(swc_path)

    densed_swc_tree = up_sample_swc_tree(swc_tree=swc_tree, thres_length=1)
    adjust_swc_tree(swc_tree=densed_swc_tree, tiff_file=test_tiff, thres_intensity=128, max_step=8)
    recall = cal_volume_recall(test_tiff=test_tiff, gold_swc=swc_tree, thres_intensity=128)

    # get_light_fig(tiff_test=test_tiff)
    print(recall)
    swc_save(densed_swc_tree, "D:\gitProject\mine\PyNeval\output\\volume_metric_test\\2_18_test.swc")
