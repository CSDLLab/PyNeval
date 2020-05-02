import math
import copy
import queue
from pyneval.model.swc_node import SwcNode,SwcTree
from pyneval.model.binary_node import BinaryNode
from pyneval.model.euclidean_point import EuclideanPoint
from pyneval.metric.utils.bin_utils import calculate_trajectories_xy,calculate_trajectories_z

_2D = "2d"

TRAJECTORY_NONE = -1.0
g_xy_threshold = 1.2
g_z_threshold = 0.0
g_default_xy_path_error_threshold = 0.05
g_default_z_path_error_threshold = 0.05
g_local_path_error_threshold = 0.4


def to_swc_node(node_a, node_b):
    if isinstance(node_a, BinaryNode):
        node_a = node_a.data
    if isinstance(node_b, BinaryNode):
        node_b = node_b.data
    return node_a, node_b


def get_end_node_XY_dis_diff(gold_swc_node,
                             trajectory,
                             test_swc_node):
    gold_dist = gold_swc_node.distance(trajectory, mode=_2D)
    test_dist = test_swc_node.distance(trajectory, mode=_2D)
    return gold_dist - test_dist


def get_end_node_Z_dis_diff(gold_swc_node,
                            trajectory,
                            test_swc_node):
    gold_dist = math.fabs(gold_swc_node.get_z() - trajectory.get_z())
    test_dist = math.fabs(test_swc_node.get_z() - trajectory.get_z())
    return gold_dist - test_dist


def get_nearby_node_list(gold_node=None, bin_test_list=None, check_previous_use=True, g_matches={}):
    nearby_node_list = []

    for test_node in bin_test_list:
        if (not check_previous_use or test_node not in g_matches.keys()) and is_in_threshold(gold_node, test_node):
            nearby_node_list.append(test_node)

    return nearby_node_list


def is_in_XY_threshold(gold_node, test_node):
    gold_node, test_node = to_swc_node(gold_node, test_node)

    xy_diff = math.sqrt((gold_node.get_x() - test_node.get_x())**2 + (gold_node.get_y() - test_node.get_y())**2)

    if xy_diff <= g_xy_threshold:
        return True
    else:
        return False


def is_in_threshold(gold_node, test_node):
    gold_node, test_node = to_swc_node(gold_node, test_node)

    xy_diff = math.sqrt((gold_node.get_x() - test_node.get_x())**2 + (gold_node.get_y() - test_node.get_y())**2)
    z_diff = math.fabs(gold_node.get_z() - test_node.get_z())

    if xy_diff <= g_xy_threshold and z_diff <= g_z_threshold + 0.1:
        return True
    else:
        return False


def get_trajectory_for_path(ancestor_node, descendant_node):
    path_stack = queue.LifoQueue()
    ancestor_data = ancestor_node.data

    while descendant_node != ancestor_node:
        path_stack.put(descendant_node)
        descendant_node = descendant_node.parent
        if descendant_node is None:
            return None

    trajectory = EuclideanPoint()

    descendant_node = path_stack.get()
    down_x = False
    down_z = False

    while not path_stack.empty() and (not down_x or not down_z):
        sec_data = descendant_node.data
        next_descendant = path_stack.get()

        if next_descendant.is_left():
            if not down_x and sec_data.left_trajectory.get_x() != TRAJECTORY_NONE:
                trajectory.set_x(sec_data.left_trajectory.get_x())
                trajectory.set_y(sec_data.left_trajectory.get_y())
                down_x = True
            if not down_z and sec_data.left_trajectory.get_z() != TRAJECTORY_NONE:
                trajectory.set_z(sec_data.left_trajectory.get_z())
                down_z = True
        elif not next_descendant.is_left() and sec_data.right_trajectory is not None:
            if not down_x and sec_data.right_trajectory.get_x() != TRAJECTORY_NONE:
                trajectory.set_x(sec_data.right_trajectory.get_x())
                trajectory.set_y(sec_data.right_trajectory.get_y())
                down_x = True
            if not down_z and sec_data.right_trajectory.get_z() != TRAJECTORY_NONE:
                trajectory.set_z(sec_data.right_trajectory.get_z())
                down_z = True

        if not down_x and not is_in_XY_threshold(ancestor_data, next_descendant.data):
            tmp = calculate_trajectories_xy(ancestor_data,
                                            descendant_node.data,
                                            next_descendant.data,
                                            g_xy_threshold)
            trajectory.set_x(tmp.get_x())
            down_x = True

        if not down_z and math.fabs(ancestor_data.get_z() - next_descendant.get_z()) > g_z_threshold:
            trajectory.set_z(calculate_trajectories_z(ancestor_data,
                                                      descendant_node.data,
                                                      next_descendant.data,
                                                      g_z_threshold))
            down_z = True
        descendant_node = next_descendant

    if not down_x:
        trajectory.set_x(descendant_node.data.get_x())
        trajectory.set_y(descendant_node.data.get_y())

    if not down_z:
        trajectory.set_z(descendant_node.data.get_z())

    return trajectory


def path_length_matches(gold_swc_path_length,
                        test_XY_path_length,
                        test_Z_path_length,
                        DEBUG = False):
    xy_path_error_threshold = g_default_xy_path_error_threshold
    z_path_error_threshold = g_default_z_path_error_threshold

    xy_diff = math.fabs(gold_swc_path_length.xy_path_length - test_XY_path_length)
    if gold_swc_path_length.path_length == 0:
        return 0
    xy_err = xy_diff / gold_swc_path_length.path_length

    if DEBUG:
        print("[Info:  ]In path length matches xy_diff = {}, xy_err = {}".format(
            xy_diff, xy_err
        ))

    z_diff = math.fabs(gold_swc_path_length.z_path_length - test_Z_path_length)
    z_err = z_diff / gold_swc_path_length.path_length

    if gold_swc_path_length.xy_path_length < g_xy_threshold:
        if test_XY_path_length < g_xy_threshold:
            xy_err = 0
        else:
            xy_path_error_threshold = g_local_path_error_threshold

    if gold_swc_path_length.z_path_length < g_z_threshold:
        if test_Z_path_length < g_z_threshold:
            z_err = 0
        else:
            z_path_error_threshold = g_local_path_error_threshold

    if xy_err < g_default_xy_path_error_threshold and z_err < g_default_z_path_error_threshold:
        return (xy_err/xy_path_error_threshold + z_err/z_path_error_threshold)/2
    else:
        return 1


def get_match_path_length_difference(gold_node, test_node, bin_gold_list, bin_test_list):
    if test_node.parent is None:
        return 0
    gold_target = gold_node

    gold_swc_path_length = SwcNode()
    gold_swc_path_length.add_length(gold_node.data)
    test_swc_path_length = SwcNode()
    test_swc_path_length.add_length(test_node.data)

    test_path_XY_mod = get_end_node_XY_dis_diff(
        gold_node.data, gold_node.data.parent_trajectory, test_node.data
    )
    test_path_Z_mod = get_end_node_Z_dis_diff(
        gold_node.data, gold_node.data.parent_trajectory, test_node.data
    )
    test_swc_path_length.xy_path_length += test_path_XY_mod
    test_swc_path_length.z_path_length += test_path_Z_mod

    is_branch_left = gold_node.is_left()
    gold_node = gold_node.parent
    test_node = test_node.parent

    ancestor_trajectory = EuclideanPoint()
    checked_node = set()
    no_match = True
    no_done = True

    while no_match and no_done:
        if is_in_threshold(gold_node, test_node):
            gold_data = gold_node.data

            if is_branch_left:
                ancestor_trajectory = gold_data.left_trajectory
            else:
                ancestor_trajectory = gold_data.right_trajectory

            if ancestor_trajectory.get_x() == TRAJECTORY_NONE or \
                ancestor_trajectory.get_z() == TRAJECTORY_NONE:
                tmp_trajectory = get_trajectory_for_path(gold_node, gold_target)
                if ancestor_trajectory.get_x() == TRAJECTORY_NONE:
                    ancestor_trajectory.set_x(tmp_trajectory.get_x())
                    ancestor_trajectory.set_y(tmp_trajectory.get_y())
                if ancestor_trajectory.get_z() == TRAJECTORY_NONE:
                    ancestor_trajectory.set_z(tmp_trajectory.get_z())

            test_XY_path_length = test_swc_path_length.xy_path_length + \
                                  get_end_node_XY_dis_diff(gold_data, ancestor_trajectory, test_node.data)
            test_Z_path_length = test_swc_path_length.z_path_length + \
                                 get_end_node_Z_dis_diff(gold_data, ancestor_trajectory, test_node.data)
            percent_error = path_length_matches(gold_swc_path_length, \
                                               test_XY_path_length, \
                                               test_Z_path_length)
            if percent_error < 1:
                return percent_error
            else:
                return 1
        else:
            if gold_swc_path_length.path_length < test_swc_path_length.path_length:
                if gold_node.parent is None:
                    no_done = False
                else:
                    nearby_nodes = get_nearby_node_list(gold_node, bin_test_list, False)
                    for node in nearby_nodes:
                        if node in checked_node:
                            no_done = False
                            break
                    checked_node.add(gold_node)
                    gold_swc_path_length.add_length(gold_node.data)
                    is_branch_left = gold_node.is_left()
                    gold_node = gold_node.parent
            else:
                if test_node.parent is None:
                    no_done = False
                else:
                    nearby_nodes = get_nearby_node_list(test_node, bin_gold_list, False)
                    for node in nearby_nodes:
                        if node in checked_node:
                            no_done = False
                            break

                    checked_node.add(test_node)
                    test_swc_path_length.add_length(test_node.data)
                    test_node = test_node.parent
    return 1


def LCA(node1, node2, kca):
    node1_list = []

    node1 = node1.parent
    while node1 != kca:
        node1_list.append(node1)
        node1 = node1.parent

    node1 = node2.parent
    while node2 != kca and node2 is not None:
        if node2 in node1_list:
            return node2
        node2 = node2.parent

    return None


def is_within_dis_match_threshold(node1, node2):
    if isinstance(node1, BinaryNode):
        node1 = node1.data
    if isinstance(node2, BinaryNode):
        node2 = node2.data
    return node1.distance(node2, _2D) <= g_xy_threshold * 3 \
           and math.fabs(node1.get_z() - node2.get_z()) < g_z_threshold * 3 + 0.1


if __name__ == "__main__":
    gold = SwcNode(center=[2,3,4])
    test = SwcNode(center=[1,-1,5])
    is_in_threshold(gold, test)