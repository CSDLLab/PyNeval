import queue
import time
import math
from src.model.binary_node import BinaryNode,RIGHT

DEBUG = False
WEIGHT_MODE = 0
WEIGHT_DEGREE = 1
WEIGHT_SQRT_DEGREE = 2
WEIGHT_DEGREE_HARMONIC_MEAN = 3
WEIGHT_PATH_LENGTH = 4
WEIGHT_UNIFORM = 5

matches = {}
remove_spur = 0

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
            if distance < threshold and not matches.__contains__(node):
                both_children_spur = False
                spur_set.add(node)
                if node.get_side() == RIGHT:
                    l_node = node.parent.left_son
                    if not l_node.has_children and l_node.data.path_length < threshold and not matches.__contains__(l_node):
                        both_children_spur = True
                        spur_set.add(l_node)
                        ll_node = stack.get()
                        if ll_node != l_node:
                            raise Exception("[Error:  ] stack top is not current node's twin")

                if not both_children_spur:
                    spur_set.add(node.parent)
    return spur_set

def generate_node_weights(bin_root, spur_set):
    init_stack = queue.LifoQueue()
    main_stack = queue.LifoQueue()
    degree_dict = {}
    weight_dict = {}
    degree = 0

    init_stack.put(bin_root)
    main_stack.put(bin_root)

    while not init_stack.empty():
        node = init_stack.get()
        if node.has_children():
            init_stack.put(node.left_son)
            init_stack.put(node.right_son)
            main_stack.put(node.left_son)
            main_stack.put(node.right_son)

    while not main_stack.empty():
        node = main_stack.get()

        if WEIGHT_MODE == WEIGHT_UNIFORM:
            weight_dict[node] = 1
        else:
            if DEBUG:
                print("Determining weight for {}".format(node.data.id))

            if node.is_leaf():
                weight_dict[node] = 1
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
                if WEIGHT_MODE == WEIGHT_DEGREE:
                    weight_dict[node] = degree
                elif WEIGHT_MODE == WEIGHT_SQRT_DEGREE:
                    weight_dict[node] = math.sqrt(degree)
                elif WEIGHT_MODE == WEIGHT_DEGREE_HARMONIC_MEAN:
                    weight_dict[node] = 2.0 / (1.0/degree_dict[node.getLeft()] + 1.0/degree_dict.get[node.getRight()])
                elif WEIGHT_MODE == WEIGHT_PATH_LENGTH:
                    weight_dict[node] = node.data.path_length
                print("nodeId = {}, degree = {}".format(node.data._id, degree))
                if node.parent is not None:
                    print("pa = {}",node.parent.data._id)
                print("-----------")

def diadem_reconstruction(bin_gold_root, bin_test_root):
    spur_set = set()
    if remove_spur > 0:
        spur_set = remove_spurs(bin_gold_root,1.0)

    generate_node_weights(bin_gold_root, spur_set)

    return 0

if __name__ == "__main__":
    diadem_reconstruction()