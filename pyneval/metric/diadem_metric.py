import queue
import time
import math
import numpy as np
import jsonschema

from anytree import PreOrderIter
from pyneval.io import read_json
from pyneval.io import read_swc
from pyneval.model import binary_node
from pyneval.model import swc_node
from pyneval.metric.utils import config_utils
from pyneval.metric.utils import diadam_match_utils
from pyneval.metric.utils import bin_utils
from pyneval.metric.utils import point_match_utils


# thresholds
g_terminal_threshold = 0

WEIGHT_DEGREE = 1
WEIGHT_SQRT_DEGREE = 2
WEIGHT_DEGREE_HARMONIC_MEAN = 3
WEIGHT_PATH_LENGTH = 4
WEIGHT_UNIFORM = 5
_2D = '2d'
_3D = '3d'

# switch
g_remove_spur = False
g_align_tree_by_root = False
g_count_excess_nodes = True
g_weight_node = WEIGHT_DEGREE
g_list_miss = False
g_list_distant_matches = False
g_list_continuations = False
g_find_proper_root = False

# various
g_weight_sum = 0
g_score_sum = 0
g_quantity_score_sum = 0
g_quantity_score = 0
g_direct_match_score = 0
g_final_score = -1

g_miss = set()
g_spur_set = set()
g_matches = {}
g_weight_dict = {}
g_excess_nodes = {}
g_distance_match = []
g_continuation = []


def remove_spurs(bin_root, threshold):
    spur_set = set()
    both_children_spur = False

    stack = queue.LifoQueue()

    if bin_root.has_children:
        stack.put(bin_root)

    while not stack.empty():
        node = stack.get()
        if node.has_children():
            stack.put(node.left_son)
            stack.put(node.right_son)
        else:
            distance = node.data.path_length
            if distance < threshold and not (node in g_matches):
                both_children_spur = False
                spur_set.add(node)
                if node.get_side() == binary_node.RIGHT:
                    l_node = node.parent.left_son
                    if not l_node.has_children and \
                            l_node.data.path_length < threshold and \
                            not l_node in g_matches:
                        both_children_spur = True
                        spur_set.add(l_node)
                        ll_node = stack.get()
                        if ll_node != l_node:
                            raise Exception("[Error:  ] stack top is not current node's twin")

                if not both_children_spur:
                    spur_set.add(node.parent)
    return spur_set


def generate_node_weights(bin_root, bin_subroot, spur_set, DEBUG=False):
    init_stack = queue.LifoQueue()
    main_stack = queue.LifoQueue()
    degree_dict = {}
    global g_weight_dict
    degree = 0
    for subroot in bin_subroot:
        init_stack.put(subroot)
        main_stack.put(subroot)

        while not init_stack.empty():
            node = init_stack.get()
            if node.has_children():
                init_stack.put(node.left_son)
                init_stack.put(node.right_son)
                main_stack.put(node.left_son)
                main_stack.put(node.right_son)

        while not main_stack.empty():
            node = main_stack.get()

            if g_weight_node == WEIGHT_UNIFORM:
                g_weight_dict[node] = 1
            else:
                if DEBUG:
                    print("Determining weight for {}".format(node.data.id))

                if node.is_leaf():
                    g_weight_dict[node] = 1
                    degree_dict[node] = 1
                else:
                    degree = 0
                    if node.left_son.is_leaf() and node.right_son.is_leaf():
                        if node.left_son in spur_set or node.right_son in spur_set:
                            degree = 1
                        else:
                            degree = 2
                    elif node in spur_set:
                        if node.left_son.is_leaf():
                            degree += degree_dict[node.right_son]
                        else:
                            degree += degree_dict[node.left_son]
                    else:
                        degree += degree_dict[node.left_son]
                        degree += degree_dict[node.right_son]
                    degree_dict[node] = degree
                    if g_weight_node == WEIGHT_DEGREE:
                        g_weight_dict[node] = degree
                    elif g_weight_node == WEIGHT_SQRT_DEGREE:
                        g_weight_dict[node] = math.sqrt(degree)
                    elif g_weight_node == WEIGHT_DEGREE_HARMONIC_MEAN:
                        g_weight_dict[node] = 2.0 / (1.0/degree_dict[node.getLeft()] + 1.0/degree_dict.get[node.getRight()])
                    elif g_weight_node == WEIGHT_PATH_LENGTH:
                        g_weight_dict[node] = node.data.path_length
                    if DEBUG:
                        print("nodeId = {}, degree = {}".format(node.data._id, degree))
                        if node.parent is not None:
                            print("pa = {}".format(node.parent.data._id))
                        print("-----------")


def is_diadem_match(gold_node, nearby_node, bin_gold_list, bin_test_list, DEBUG=False):
    length_diff = diadam_match_utils.get_match_path_length_difference(gold_node,
                                                                      nearby_node,
                                                                      bin_gold_list,
                                                                      bin_test_list)
    if DEBUG:
        print("gold_node = {}, test_node = {}, length_diff = {}".format(
            gold_node.data.get_id(), nearby_node.data.get_id(), length_diff
        ))
    if length_diff < 1:
        return True
    else:
        return False


def get_best_match(match_list, gold_node, bin_test_list,DEBUG=False):
    if DEBUG:
        print("Determining best match")
    confirm_list = []

    gold_data = gold_node.data
    des_branch_left = {}
    trajactory_map = {}

    if gold_node.has_children():
        nearby_list = []
        path_length_map = {}
        path_length_map[gold_node] = swc_node.SwcNode()

        target_dis_list = []
        for test_node in match_list:
            target_distances = swc_node.SwcNode()
            target_distances.xy_path_length = gold_node.data.distance(test_node.data, _2D)
            target_distances.z_path_length = gold_node.data.distance(test_node.data, _2D)
            target_dis_list.append(target_distances)

        current_list = []
        current_list.append(gold_node.left_son)
        trajactory_map[gold_node.left_son] = gold_node.data.left_trajectory
        des_branch_left[gold_node.left_son] = True

        current_list.append(gold_node.right_son)
        trajactory_map[gold_node.right_son] = gold_node.data.right_trajectory
        des_branch_left[gold_node.right_son] = False

        while len(current_list) > 0 and len(confirm_list) == 0:
            next_list = []
            for des_node in current_list:
                target_tra = trajactory_map[des_node]

                if target_tra.get_x() == -1.0 or target_tra.get_z() == -1.0:
                    tmp_tra = diadam_match_utils.get_trajectory_for_path(gold_node, des_node)
                    if target_tra.get_x() == -1.0:
                        target_tra.set_x(tmp_tra.get_x())
                        target_tra.set_y(tmp_tra.get_y())
                    if target_tra.get_z() == -1.0:
                        target_tra.set_z(tmp_tra.get_z())
                des_tra = des_node.data.parent_trajectory

                if des_node.has_children():
                    next_list.append(des_node.left_son)
                    next_list.append(des_node.right_son)
                    trajactory_map[des_node.left_son] = target_tra
                    trajactory_map[des_node.right_son] = target_tra

                gold_path_length = swc_node.SwcNode()
                gold_path_length.add_length(des_node.data)
                parent_path_length = path_length_map[des_node.parent]
                gold_path_length.add_length(parent_path_length)
                path_length_map[des_node] = gold_path_length

                nearby_list = diadam_match_utils.get_nearby_node_list(des_node,
                                                                      bin_test_list,
                                                                      check_previous_use=True,
                                                                      g_matches=g_matches)

                for test_node in nearby_list:
                    test_des_node = test_node
                    test_path_length = swc_node.SwcNode()

                    des_dis = swc_node.SwcNode()
                    des_dis.xy_path_length = des_node.data.distance(test_node.data, _2D)
                    des_dis.z_path_length = math.fabs(des_node.data.get_z() - test_node.data.get_z())

                    while test_node.parent is not None:
                        test_path_length.add_length(test_node.data)
                        test_node = test_node.parent
                        tmp_list = []
                        for match in match_list:
                            if test_node == match:
                                test_XY_path_length = test_path_length.xy_path_length + \
                                                      diadam_match_utils.get_end_node_XY_dis_diff(gold_data, target_tra, test_node.data) + \
                                                      diadam_match_utils.get_end_node_XY_dis_diff(des_node.data, des_tra, test_des_node.data)
                                test_Z_path_length = test_path_length.z_path_length + \
                                                     diadam_match_utils.get_end_node_Z_dis_diff(gold_data, target_tra, test_node.data) + \
                                                     diadam_match_utils.get_end_node_Z_dis_diff(des_node.data, des_tra, test_des_node.data)

                                if diadam_match_utils.path_length_matches(gold_path_length,
                                                                          test_XY_path_length,
                                                                          test_Z_path_length) < 1:
                                    confirm_list.append(match)
                                    tmp_list.append(match)

                        for node in tmp_list:
                            match_list.remove(node)
                        while len(tmp_list):
                            tmp_list.pop()

            current_list = nearby_list
    if len(confirm_list) == 1:
        return confirm_list[0]

    if len(confirm_list) == 0:
        confirm_list = match_list

    dis = 0
    closest_dis = -1
    closest_match = None
    for test_node in confirm_list:
        dis = test_node.data.distance(gold_node.data)
        if closest_dis == -1 or dis < closest_dis:
            closest_dis = dis
            closest_match = test_node

    return closest_match


def get_closest_match(gold_node,
                      bin_gold_list,
                      bin_test_list,
                      DEBUG=False):
    best_match = None

    # Step1: find node within threshold
    nearby_list = diadam_match_utils.get_nearby_node_list(gold_node=gold_node,
                                                          bin_test_list=bin_test_list,
                                                          check_previous_use=True,
                                                          g_matches=g_matches)
    if DEBUG:
        print("nearby list of {}:".format(gold_node.data.get_id()))
        for node in nearby_list:
            print(node.data.get_id())
        print("----END----")

    # Step2: find match node whose ancestor is also matched
    match_list = []
    for nearby_node in nearby_list:
        if is_diadem_match(gold_node, nearby_node, bin_gold_list, bin_test_list):
            if DEBUG:
                print("{} {}".format(
                    gold_node.data.get_id(), nearby_node.data.get_id()
                ))
            match_list.append(nearby_node)

    if len(match_list) == 1:
        best_match = match_list[0]
    elif len(match_list) >= 1:
        best_match = get_best_match(match_list, gold_node, bin_test_list)

    if DEBUG:
        if best_match is not None:
            print("best match {} {}".format(gold_node.data.get_id(), best_match.data.get_id()))
        else:
            print("best match {} None".format(gold_node.data.get_id()))
    return best_match


def get_des_in_for_continuation(first_node, ancestor_node, ancestor_match,
                                ancestor_trajectory,path_length_map,bin_test_list,DEBUG=False):
    spe_ancestor_trajectory = ancestor_trajectory
    test_matches = []

    stack = queue.LifoQueue()
    stack.put(first_node)
    while not stack.empty():
        gold_node = stack.get()
        des_tra = gold_node.data.parent_trajectory
        # print("gold_node id = {}".format(gold_node.data.get_id()))
        if gold_node in g_matches:
            test_matches.append(g_matches[gold_node])
        else:
            test_matches = diadam_match_utils.get_nearby_node_list(gold_node,
                                                                   bin_test_list,
                                                                   check_previous_use=False)

        prev_path_length = path_length_map[gold_node.parent]
        gold_path_length = swc_node.SwcNode()
        gold_path_length.path_length = gold_node.data.path_length + prev_path_length.path_length
        gold_path_length.xy_path_length = gold_node.data.xy_path_length + prev_path_length.xy_path_length
        gold_path_length.z_path_length = gold_node.data.z_path_length + prev_path_length.z_path_length
        path_length_map[gold_node] = gold_path_length

        for child_match in test_matches:
            test_path_length = swc_node.SwcNode()
            test_path_length.add_data(child_match.data)
            tmp_node = child_match.parent
            # print("child match id = {}".format(
            #     child_match.data.get_id()))
            done = (tmp_node == ancestor_match)
            while not done:
                if tmp_node in path_length_map.keys():
                    prev_path_length = path_length_map[tmp_node]
                    test_path_length.add_length(prev_path_length)
                    done = True
                else:
                    test_path_length.add_length(tmp_node.data)
                    tmp_node = tmp_node.parent
                    if tmp_node is None:
                        done = True

                if tmp_node == ancestor_match:
                    done = True

            if tmp_node is None:
                if DEBUG:
                    print("[info]: descendant not match")
            else:
                path_length_map[child_match] = test_path_length
                if ancestor_trajectory.get_x() == -1.0 or ancestor_trajectory.get_z() == -1.0:
                    spe_ancestor_trajectory = diadam_match_utils.get_trajectory_for_path(ancestor_node, gold_node)
                    if ancestor_trajectory.get_x != -1.0:
                        spe_ancestor_trajectory.set_x(ancestor_trajectory.get_x())
                        spe_ancestor_trajectory.set_y(ancestor_trajectory.get_y())
                    if ancestor_trajectory.get_z != -1.0:
                        spe_ancestor_trajectory.set_z(ancestor_trajectory.get_z())

                test_xy_path_length = test_path_length.xy_path_length \
                                      + diadam_match_utils.get_end_node_XY_dis_diff(ancestor_node.data,
                                                                                    spe_ancestor_trajectory,
                                                                                    ancestor_match.data) \
                                      + diadam_match_utils.get_end_node_XY_dis_diff(gold_node.data,
                                                                                    des_tra,
                                                                                    child_match.data)
                test_z_path_length = test_path_length.z_path_length \
                                      + diadam_match_utils.get_end_node_Z_dis_diff(ancestor_node.data,
                                                                                   spe_ancestor_trajectory,
                                                                                   ancestor_match.data) \
                                      + diadam_match_utils.get_end_node_Z_dis_diff(gold_node.data,
                                                                                   des_tra,
                                                                                   child_match.data)

                if diadam_match_utils.path_length_matches(gold_path_length,
                                                          test_xy_path_length,
                                                          test_z_path_length) < 1:
                    return child_match

        if gold_node.has_children() and gold_node not in g_matches:
            stack.put(gold_node.left_son)
            stack.put(gold_node.right_son)

    return None


def is_sub_continuation(gold_node, ancestor_node, ancestor_match,
                        is_left, gold_path_length, bin_test_list, add_to_list):
    if ancestor_match is None:
        return False

    path_length_map = {}
    path_length_map[gold_node] = gold_path_length

    if is_left:
        ancestor_tra = ancestor_node.data.left_trajectory
    else:
        ancestor_tra = ancestor_node.data.right_trajectory

    left_child_match = get_des_in_for_continuation(
        gold_node.left_son, ancestor_node, ancestor_match, ancestor_tra, path_length_map, bin_test_list
    )
    right_child_match = get_des_in_for_continuation(
        gold_node.right_son, ancestor_node, ancestor_match, ancestor_tra, path_length_map, bin_test_list
    )

    if left_child_match is not None and right_child_match is not None:
        common_ancestor = diadam_match_utils.LCA(left_child_match, right_child_match, ancestor_match)
        if common_ancestor is not None and diadam_match_utils.is_within_dis_match_threshold(common_ancestor, gold_node):
            g_matches[gold_node] = common_ancestor
            g_matches[common_ancestor] = gold_node
            if add_to_list:
                g_distance_match.append(gold_node)
        elif add_to_list:
            g_continuation.append(gold_node)
        return True
    elif left_child_match is not None or right_child_match is not None:
        if add_to_list:
            g_continuation.append(gold_node)
        return True
    return False


def is_continuation(gold_node, bin_test_list, add_to_list=True, DEBUG=False):
    if not gold_node.has_children():
        return False

    ancestor_node_matches = []
    gold_path_length = swc_node.SwcNode()

    # find the first matched ancestor of the gold_node
    ancestor_match = None
    ancestor_gold = gold_node.parent
    gold_path_length.path_length = gold_node.data.path_length
    gold_path_length.xy_path_length = gold_node.data.xy_path_length
    gold_path_length.z_path_length = gold_node.data.z_path_length
    is_match = False
    ancestor_match = False
    is_left = False

    if DEBUG:
        print("gold_path_length: path_length {}, xy_path_length {}, z_path_length {}".format(
            gold_path_length.path_length,
            gold_path_length.xy_path_length,
            gold_path_length.z_path_length
        ))
    while ancestor_gold is not None and not ancestor_match:
        if ancestor_gold in g_matches.keys():
            ancestor_match = g_matches[ancestor_gold]
            if is_sub_continuation(gold_node, ancestor_gold, ancestor_match,is_left,
                                   gold_path_length, bin_test_list, add_to_list):
                return True
            ancestor_match = True
        ancestor_node_matches = diadam_match_utils.get_nearby_node_list(ancestor_gold, bin_test_list, check_previous_use=True, g_matches=g_matches)
        for a_n_node in ancestor_node_matches:
            if is_sub_continuation(gold_node, ancestor_gold, ancestor_match, is_left,
                                   gold_path_length, bin_test_list, add_to_list):
                return True

        gold_path_length.path_length += ancestor_gold.data.path_length
        gold_path_length.xy_path_length += ancestor_gold.data.xy_path_length
        gold_path_length.z_path_length += ancestor_gold.data. z_path_length
        is_left = ancestor_gold.is_left()
        ancestor_gold = ancestor_gold.parent

    # failed
    return False


def get_excess_weight(excess, node, excess_map):
    if g_weight_node == WEIGHT_SQRT_DEGREE:
        return math.sqrt(excess)
    if g_weight_node == WEIGHT_DEGREE_HARMONIC_MEAN:
        return 2.0/(1.0/excess_map[node.left_son] + 1.0/excess_map[node.right_son])
    if g_weight_node == WEIGHT_UNIFORM:
        return excess > 0
    if g_weight_node == WEIGHT_DEGREE:
        return excess


def remove_nearest_node(node, nearby_nodes, bin_gold_list):
    closest_dis = -1
    closest_match = None

    for nearby_node in nearby_nodes:
        dis = node.data.distance(nearby_node.data)
        if closest_dis == -1 or dis < closest_dis:
            closest_dis = dis
            closest_match = nearby_node

    bin_gold_list.remove(closest_match)


def weight_excess(bin_gold_subroot, bin_test_subroot, DEBUG=False):
    global g_excess_nodes

    if DEBUG:
        for node in g_matches.keys():
            print("matches = {}".format(node.data.get_id()))

    sum_weight = 0.0
    gold_bin_list = []
    setup_stack = queue.LifoQueue()
    use_stack = queue.LifoQueue()

    for son in bin_gold_subroot:
        gold_bin_list.extend(son.get_node_list())

    for son in bin_test_subroot:
        setup_stack.put(son)
        use_stack.put(son)
        while not setup_stack.empty():
            node = setup_stack.get()
            if node.has_children():
                setup_stack.put(node.left_son)
                setup_stack.put(node.right_son)
                use_stack.put(node.left_son)
                use_stack.put(node.right_son)

        direct_term_excess = {}

        while not use_stack.empty():
            node = use_stack.get()
            data = node.data
            # if data.get_id()
            if DEBUG:
                print("{} sum weight {}".format(
                    data.get_id(),
                    sum_weight
                ))

            if node.has_children():
                num_excess_node = direct_term_excess[node.left_son]
                num_excess_node += direct_term_excess[node.right_son]
                excess_weight = get_excess_weight(num_excess_node, node, direct_term_excess)

                if not node in g_matches.keys() and \
                        len(diadam_match_utils.get_nearby_node_list(node, gold_bin_list,
                                                                    check_previous_use=True, g_matches=g_matches)) == 0 and \
                        not is_continuation(node, gold_bin_list, add_to_list=False):
                    g_excess_nodes[node] = excess_weight
                    if not node in g_spur_set:
                        sum_weight += excess_weight
                else:
                    num_excess_node = 0
                    excess_weight = 0
            else:
                num_excess_node = 0
                excess_weight = 0

                if node not in g_spur_set and node not in g_matches.keys() and node.parent not in g_matches.keys():
                    nearby_nodes = diadam_match_utils.get_nearby_node_list(node, gold_bin_list,
                                                                           check_previous_use=True, g_matches = g_matches)
                    if len(nearby_nodes) > 0:
                        remove_nearest_node(node, nearby_nodes, gold_bin_list)
                    else:
                        num_excess_node = 1
                        excess_weight = 1
                        g_excess_nodes[node] = 1
                        sum_weight += excess_weight

            direct_term_excess[node] = num_excess_node
    return sum_weight


def score_trees(bin_gold_root, bin_test_root, bin_gold_subroots, bin_test_subroots, DEBUG=False):
    global g_weight_dict
    global g_weight_sum
    global g_score_sum
    global g_quantity_score_sum
    global g_final_score
    global g_direct_match_score
    global g_quantity_score

    stack = queue.LifoQueue()
    number_of_nodes = 0
    weight = 0

    bin_test_list = []
    bin_gold_list = []

    # Root is certainly matched, note that here is a address use
    bin_gold_root.data.parent_trajectory = bin_gold_root.data.get_center()
    bin_gold_root.data.left_trajectory = bin_gold_root.data.get_center()
    bin_gold_root.data.right_trajectory = bin_gold_root.data.get_center()
    if bin_test_root is not None:
        bin_test_root.data.parent_trajectory = bin_test_root.data.get_center()
        bin_test_root.data.left_trajectory = bin_test_root.data.get_center()
        bin_test_root.data.right_trajectory = bin_test_root.data.get_center()

        g_matches[bin_gold_root] = bin_test_root
        g_matches[bin_test_root] = bin_gold_root

        for son in bin_test_subroots:
            son.parent = bin_test_root
            bin_test_list.extend(son.get_node_list())

    for son in bin_gold_subroots:
        son.parent = bin_gold_root
        bin_gold_list.extend(son.get_node_list())

    # Increment quantity (non-continuations)
    g_quantity_score_sum += 1

    number_of_nodes -= len(g_spur_set)
    number_of_nodes += len(bin_gold_list)

    for gold_subroot in bin_gold_subroots:
        stack.put(gold_subroot)

        while not stack.empty():
            gold_node = stack.get()
            gold_data = gold_node.data
            if DEBUG:
                print(gold_node.data.get_id())
                if gold_node.data.get_id() in [4,5,6,7]:
                    print("line:616")

            if gold_node.has_children():
                stack.put(gold_node.left_son)
                stack.put(gold_node.right_son)

            if gold_node in g_spur_set:
                pass
            else:
                weight = g_weight_dict[gold_node]
                g_weight_sum += weight
                match = get_closest_match(gold_node=gold_node,
                                          bin_gold_list=bin_gold_list,
                                          bin_test_list=bin_test_list)

                # another match method (temporarily undo)
                # if match is None and gold_node.is_leaf() and g_terminal_threshold > 0:
                #     match = get_extended_termination_match(gold_node = gold_node,
                #                                            bin_gold_list = bin_gold_list,
                #                                            bin_test_list = bin_test_list)

                if match is not None:
                    g_matches[gold_node] = match
                    g_matches[match] = gold_node
                    g_score_sum += weight

                    # Increment quantity (non-continuations)
                    g_quantity_score_sum += 1
                else:
                    g_miss.add(gold_node)
        if DEBUG:
            gold_subroot.print_tree()
            print("--END--\n")
            if gold_subroot in g_matches.keys() is not None:
                g_matches[gold_subroot].print_tree()
    t_remove = []

    for miss_node in g_miss:
        if miss_node.left_son is not None or miss_node.right_son is not None:
            if is_continuation(miss_node, bin_test_list):
                weight = g_weight_dict[miss_node]
                g_score_sum += weight
                if DEBUG:
                    print("[Info: ] find continuation in miss nodes {}".format(miss_node.to_str()))
                t_remove.append(miss_node)

    for node in t_remove:
        g_miss.remove(node)

    if g_weight_sum > 0:
        try:
            g_direct_match_score = g_quantity_score_sum / number_of_nodes
        except ZeroDivisionError:
            g_direct_match_score = 0
        try:
            g_quantity_score = g_score_sum / g_weight_sum
        except ZeroDivisionError:
            g_quantity_score = 0

        if g_remove_spur > 0:
            remove_spurs(bin_test_root)

        if g_count_excess_nodes:
            g_weight_sum += weight_excess(bin_gold_subroots, bin_test_subroots)

        try:
            g_final_score = g_score_sum / g_weight_sum
        except ZeroDivisionError:
            g_final_score = 0


def config_init(config):
    """
    Read data in config to global
    Args:
        None
    Returns:
        None
    """
    global g_remove_spur
    global g_align_tree_by_root
    global g_count_excess_nodes
    global g_weight_node
    global g_list_miss
    global g_list_distant_matches
    global g_list_continuations
    global g_find_proper_root

    if "remove_spur" in config:
        g_remove_spur = config["remove_spur"]
    if "align_tree_by_root" in config.keys():
        g_align_tree_by_root = config["align_tree_by_root"]
    if "count_excess_nodes" in config.keys():
        g_count_excess_nodes = config["count_excess_nodes"]
    if "weight_node" in config.keys():
        g_weight_node = config["weight_node"]
    if "list_miss" in config.keys():
        g_list_miss = config["list_miss"]
    if "list_distant_matches" in config.keys():
        g_list_distant_matches = config["list_distant_matches"]
    if "list_continuations" in config.keys():
        g_list_continuations = config["list_continuations"]
    if "find_proper_root" in config.keys():
        g_find_proper_root = config["find_proper_root"]


def diadem_init():
    """
    init global parameters of diadem metric
    Args:
        None
    Returns:
        None
    """
    global g_weight_sum
    global g_score_sum
    global g_quantity_score_sum
    global g_quantity_score
    global g_direct_match_score
    global g_final_score
    global g_miss
    global g_spur_set
    global g_matches
    global g_weight_dict
    global g_excess_nodes
    global g_distance_match
    global g_continuation

    g_weight_sum = 0
    g_score_sum = 0
    g_quantity_score_sum = 0
    g_quantity_score = 0
    g_direct_match_score = 0
    g_final_score = -1

    g_miss = set()
    g_spur_set = set()
    g_matches = {}
    g_weight_dict = {}
    g_excess_nodes = {}
    g_distance_match = []
    g_continuation = []


def color_tree_only():
    if g_list_miss:
        if len(g_miss) > 0:
            for node in g_miss:
                # 9 means this node is missed
                node.data._type = 9
        if len(g_excess_nodes) > 0:
            for node in g_excess_nodes.keys():
                # 10 means this node is excessive
                node.data._type = 10

    if g_list_continuations:
        if len(g_continuation) > 0:
            for node in g_continuation:
                # 11 means this node is a continuation
                node.data._type = 11

    if g_list_distant_matches:
        if len(g_distance_match) > 0:
            for node in g_distance_match:
                # 12 means this node is a distant match
                node.data._type = 12


def print_result():
    start = time.time()
    print("g_weight_sum = {}".format(
        g_weight_sum
    ))
    print("g_score_sum = {}".format(
        g_score_sum
    ))
    print("g_final_score = {}".format(
        g_final_score
    ))
    print("time cost = {}".format(
        time.time() - start)
    )
    if g_list_miss:
        if len(g_miss) > 0:
            print("---Nodes that are missed (position and weight)---")
            for node in g_miss:
                print("node_ID = {} poi = {} weight = {}".format(
                    node.data.get_id(), node.data._pos, g_weight_dict[node]
                ))
                # 9 means this node is missed
                node.data._type = 9
            print("--END--")
        else:
            print("---Nodes that are missed:None---")

        print("")

        if len(g_excess_nodes) > 0:
            print("---extra Nodes in test reconstruction (position and weight)---")
            for node in g_excess_nodes.keys():
                print("node_ID = {} poi = {} weight = {}".format(
                    node.data.get_id(), node.data._pos, g_excess_nodes[node]
                ))
                # 10 means this node is excessive
                node.data._type = 10
        else:
            print("---extra Nodes in test reconstruction: None---")

    if g_list_continuations:
        print("")
        if len(g_continuation) > 0:
            print("---continuation Nodes (position and weight)---")
            for node in g_continuation:
                print("node_ID = {} poi = {} weight = {}".format(
                    node.data.get_id(), node.data._pos, g_weight_dict[node]
                ))
                # 11 means this node is a continuation
                node.data._type = 11
        else:
            print("---continuation Nodes None---")

    if g_list_distant_matches:
        print("")
        if len(g_distance_match) > 0:
            print("Distant Matches")
            for node in g_distance_match:
                print("node_ID = {} poi = {} weight = {}".format(
                    node.data.get_id(), node.data._pos, g_weight_dict[node]
                ))
                # 12 means this node is a distant match
                node.data._type = 12
        else:
            print("Distant Matches: none")


def adjust_root(swc_gold_tree, swc_test_tree,
                test_kdtree, test_pos_node_dict, t_matches):
    """
    find a common root for both gold and test trees
    Args:
        swc_gold_tree(Swc_Tree):
        swc_test_tree(Swc_Tree):
        test_kdtree(kd tree established based on test tree)
        test_pos_node_dict(Dict): a dict of test tree
            keys: tuple(x, y, z)
            value: Swc_Node in position of tuple
        t_matches(Dict):
            A match Dict of nodes in gold test
            key: Swc Node in gold tree
            value: Swc Node in test tree
    """
    swc_gold_list = swc_gold_tree.get_node_list()
    swc_test_list = swc_test_tree.get_node_list()

    gold_vis_list = np.zeros(shape=(len(swc_gold_list) + 10,))
    test_vis_list = np.zeros(shape=(len(swc_test_list) + 10,))

    for node in swc_gold_list:
        if node.is_virtual():
            continue
        nearby_nodes = swc_node.get_nearby_swc_node_list(gold_node=node, threshold=node.radius() / 2,
                                                         test_kdtree=test_kdtree, test_pos_node_dict=test_pos_node_dict)
        for t_node in nearby_nodes:
            if not gold_vis_list[node.get_id()] and not test_vis_list[t_node.get_id()]:
                t_matches[node] = t_node
                swc_gold_tree.change_root(node.get_id())
                swc_test_tree.change_root(t_node.get_id())

                for sub_node in PreOrderIter(node):
                    gold_vis_list[sub_node.get_id()] = 1
                for sub_node in PreOrderIter(t_node):
                    test_vis_list[sub_node.get_id()] = 1
                break


def diadem_metric(gold_swc_tree, test_swc_tree, config):
    """Main function of diadem metric
    Args:
        gold_swc_tree(SwcTree):
        test_swc_tree(SwcTree):
        config(Dict):
            The keys of 'config' is the name of configs, and the items are config values

    Example:
        test_tree = swc_node.SwcTree()
        gold_tree = swc_node.SwcTree()
        gold_tree.load("..\\..\\data\\test_data\\topo_metric_data\\sgold_fake_data2.swc")
        test_tree.load("..\\..\\data\\test_data\\topo_metric_data\\stest_fake_data2.swc")
        score, recall, precision = ssd_metric(gold_swc_tree=gold_tree,
                                              test_swc_tree=test_tree,
                                              config=config)

    Return:
        tuple: contain three values to demonstrate metric result
            g_weight_sum(float): weight of all nodes in the gold tree
            g_score_sum(float): weight of all the nodes that are matched.
            g_final_score(float): ratio of above two value

    Raise:
        None
    """
    global g_spur_set
    global g_weight_dict
    gold_swc_tree.set_node_type_by_topo(root_id=1)
    test_swc_tree.set_node_type_by_topo(root_id=5)
    diadem_init()
    config_init(config)
    diadam_match_utils.diadem_utils_init(config)
    scale = config["scale"]
    gold_swc_tree.rescale(scale)
    test_swc_tree.rescale(scale)
    test_kdtree, test_pos_node_dict = point_match_utils.create_kdtree(test_swc_tree.get_node_list())

    t_matches = {}
    debug = False
    if g_find_proper_root:
        adjust_root(swc_gold_tree=gold_swc_tree, swc_test_tree=test_swc_tree,
                    test_kdtree=test_kdtree, test_pos_node_dict=test_pos_node_dict,
                    t_matches=t_matches)
    if g_align_tree_by_root:
        test_swc_tree.align_roots(gold_tree=gold_swc_tree, t_matches=t_matches)

    # the id of root here is always -1, so we need to figure out first level sons of root
    for sub_gold_root in gold_swc_tree.root().children:
        if sub_gold_root in t_matches.keys():
            sub_test_root = t_matches[sub_gold_root]
            bin_test_root, bin_test_list = bin_utils.convert_to_binarytrees(sub_test_root)
        else:
            bin_test_root, bin_test_list = None, []

        bin_gold_root, bin_gold_list = bin_utils.convert_to_binarytrees(sub_gold_root)

        if g_remove_spur > 0:
            g_spur_set = remove_spurs(bin_gold_root, 1.0)

        generate_node_weights(bin_gold_root, bin_gold_list, g_spur_set)
        score_trees(bin_gold_root,
                    bin_test_root,
                    bin_gold_list,
                    bin_test_list)

        # debug
        if debug:
            for key in g_matches:
                print('match1 = {}, match2 = {}'.format(
                    key.data.get_id(), g_matches[key].data.get_id()
                ))
    color_tree_only()
    if debug:
        for k in g_weight_dict:
            print("id = {} wt = {}".format(k.data.get_id(), g_weight_dict[k]))

    if config['debug'] is True:
        print_result()

    res = {
        "weight_sum": g_weight_sum,
        "score_sum": g_score_sum,
        "final_score": g_final_score
    }
    return res, gold_swc_tree, test_swc_tree


def pyneval_diadem_metric(gold_swc, test_swc, config):
    """ interface to webmets, which is a web visualization project abandoned now
    Args: Same as func:diadem_metric
        gold_swc_tree(SwcTree):
        test_swc_tree(SwcTree):
        config(Dict):
            The keys of 'config' is the name of configs, and the items are config values
    Return:
        result(Dict): contain several metric results
    """
    gold_tree = swc_node.SwcTree()
    test_tree = swc_node.SwcTree()

    gold_tree.load_list(read_swc.adjust_swcfile(gold_swc))
    test_tree.load_list(read_swc.adjust_swcfile(test_swc))

    diadem_res = diadem_metric(gold_swc_tree=gold_tree,
                              test_swc_tree=test_tree,
                              config=config)

    result = {
        'gold_swc': gold_tree.to_str_list(),
        'test_swc': test_tree.to_str_list(),
        'weight_sum': diadem_res[0],
        'score_sum': diadem_res[1],
        'final_score': diadem_res[2]
    }

    return result


if __name__ == "__main__":
    start_time = time.time()
    testTree = swc_node.SwcTree()
    goldTree = swc_node.SwcTree()

    goldTree.load("../../data/test_data/topo_metric_data/gold_fake_data3.swc")
    testTree.load("../../data/test_data/topo_metric_data/test_fake_data3.swc")
    config_utils.get_default_threshold(goldTree)
    config = read_json.read_json("../../config/diadem_metric.json")
    config_schema = read_json.read_json("../../config/schemas/diadem_metric_schema.json")

    try:
        jsonschema.validate(config, config_schema)
    except Exception as e:
        raise Exception("[Error: ]Error in analyzing config json file")

    diadem_result, tmp1, tmp2 = diadem_metric(test_swc_tree=testTree,
                                              gold_swc_tree=goldTree,
                                              config=config)
    print("matched weight = {}\n"
          "total weight   = {}\n"
          "diadem score   = {}\n".
          format(diadem_result["weight_sum"], diadem_result["score_sum"], diadem_result["final_score"]))
