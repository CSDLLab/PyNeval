import jsonschema
import queue
import math

from pyneval.metric.utils.klib.TiffFile import imread
from pyneval.model.swc_tree import SwcTree
from pyneval.tools.re_sample import up_sample_swc_tree

from pyneval.metric.utils.metric_manager import get_metric_manager

metric_manager = get_metric_manager()

class VolumeMetric(object):
    """
    volume metric
    """

    def __init__(self, config):
        self.debug = config["debug"] if config.get("debug") is not None else False
        self.length_threshold = config['length_threshold']
        self.intensity_threshold = config['intensity_threshold']

    def adjust_swc_tree(self, swc_tree, tiff_file, thres_intensity, max_step=4):
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

    @staticmethod
    def get_dis(tuple_1, tuple_2):
        dx = tuple_1[0] - tuple_2[0]
        dy = tuple_1[1] - tuple_2[1]
        dz = tuple_1[2] - tuple_2[2]
        return math.sqrt(dx**2 + dy**2 + dz**2)

    def cal_label(self, node, test_tiff, thres_intensity, max_step=0):
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
        return None


    def cal_volume_recall(self, test_tiff, gold_swc, intensity_threshold):
        swc_node_list = gold_swc.get_node_list()
        tot_front, tot_back = 0, 0

        for node in swc_node_list:
            if node.is_virtual():
                continue
            if (len(node.children) == 0 or node.parent.is_virtual()) and\
                    self.cal_label(node, test_tiff, intensity_threshold, 0) is not None:
                tot_front += 1
            elif self.cal_label(node, test_tiff, intensity_threshold, 1) is not None:
                tot_front += 1
            else:
                if self.debug:
                    print("[Info: ] fail: {} {} {} {} {}".format(
                        node.get_id(), round(node.get_x()), round(node.get_y()), round(node.get_z()),
                        test_tiff[round(node.get_z())][round(node.get_y())][round(node.get_x())]
                    ))

            tot_back += 1
        return tot_front/tot_back

    def run(self, gold_swc_tree, test_swc_tree):

        densed_swc_tree = up_sample_swc_tree(swc_tree=gold_swc_tree, length_threshold=self.length_threshold)
        recall = self.cal_volume_recall(test_swc_tree, densed_swc_tree, self.intensity_threshold)

        res = {
            "recall": recall
        }
        return res, None, None


@metric_manager.register(
    name="volume",
    config="volume_metric.json",
    desc="volume overlap",
    public=False,
    alias=['VM']
)
def volume_metric(gold_swc_tree, test_swc_tree, config):
    volume = VolumeMetric(config)
    return volume.run(gold_swc_tree, test_swc_tree)
