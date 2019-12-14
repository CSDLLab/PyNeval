import queue
import kdtree
from anytree import PreOrderIter

def get_kdtree_data(kd_node):
    return kd_node[0].data


def check_match(gold_node_knn, son_node_knn, edge_set, id_center_dict):
    for pa in gold_node_knn:
        test_pa_node = id_center_dict[tuple(get_kdtree_data(pa))]
        for tpn in test_pa_node:
            for sn in son_node_knn:
                test_son_node = id_center_dict[tuple(get_kdtree_data(sn))]
                for tsn in test_son_node:
                    if tuple([tpn, tsn]) in edge_set:
                        edge_set.remove(tuple([tpn, tsn]))
                        edge_set.remove(tuple([tsn, tpn]))
                        return tuple([tpn, tsn])
    return None


def get_match_edges_p(gold_swc_tree=None, test_swc_tree=None, knn=3, DEBUG=False):
    match_edge = {}
    test_swc_list = [node for node in PreOrderIter(test_swc_tree.root())]
    if DEBUG:
        for item in test_swc_list:
            print("---{} {}".format(item.get_id(), item._pos))
    id_center_dict = {}
    center_list = []
    edge_set = set()
    global dis_threshold
    for node in test_swc_list:
        if node.is_virtual():
            continue
        if tuple(node._pos) not in id_center_dict.keys():
            id_center_dict[tuple(node._pos)] = []
        id_center_dict[tuple(node._pos)].append(node)
        center_list.append(node._pos)
        for son in node.children:
            edge_set.add(tuple([node, son]))
            edge_set.add(tuple([son, node]))

    test_kdtree = kdtree.create(center_list)

    stack = queue.LifoQueue()
    stack.put(gold_swc_tree.root())
    while not stack.empty():
        gold_node = stack.get()
        for son in gold_node.children:
            stack.put(son)

        if gold_node.is_virtual():
            continue

        gold_node_knn = test_kdtree.search_knn(gold_node._pos, knn)

        for node in gold_node_knn:
            if gold_node.distance(get_kdtree_data(node)) > dis_threshold:
                gold_node_knn.remove(node)
        if DEBUG:
            print("knn of gold = {}".format(gold_node_knn))
        for son in gold_node.children:
            son_node_knn = test_kdtree.search_knn(son._pos, knn)
            if DEBUG:
                print("son of gold = {}".format(son_node_knn))
            match = check_match(gold_node_knn, son_node_knn, edge_set, id_center_dict)
            if match is not None:
                match_edge[tuple([gold_node, son])] = match

    return match_edge