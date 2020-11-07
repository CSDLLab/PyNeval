import numpy as np
from pyneval.metric.utils.config_utils import EPS, DINF


def get_simple_lca_length(std_tree, test_gold_dict, node1, node2, switch):
    if std_tree.depth_array is None:
        raise Exception("[Error: ] std has not been lca initialized yet")
    std_id_node_dict = std_tree.get_id_node_dict()
    if switch:
        tmp_node1 = node1
        tmp_node2 = test_gold_dict[node2]
    else:
        tmp_node1 = test_gold_dict[node1]
        tmp_node2 = node2
    if tmp_node1 is None or tmp_node2 is None:
        raise Exception("[Error: ]gold tree and test tree are not same. ")

    lca_id = std_tree.get_lca(tmp_node1.get_id(), tmp_node2.get_id())
    if lca_id == -1:
        return DINF
    lca_node = std_id_node_dict[lca_id]
    return tmp_node1.root_length + tmp_node2.root_length - 2 * lca_node.root_length


def get_dis_graph(gold_tree, test_tree, test_node_list, gold_node_list,
                  test_gold_dict, threshold_dis, metric_mode=1):
    """
    We use KM algorithm to get the minimum full match between gold and test branch&leaf nodes
    Since KM is used for calculating maximum match, we use the opposite value of distance
    mode = 1: distance between nodes are calculated as euclidean distance
    mode = 2: distance between nodes are calculated as distance on the gold tree
    """
    std_tree = gold_tree

    if metric_mode == 2:
        if std_tree.depth_array is None:
            std_tree.get_lca_preprocess()

    # KM works only when the length of the first dimensionality is SMALLER than the second one
    # so we need to switch gold and test when gold list is SMALLER
    switch = False
    test_len = len(test_node_list)
    gold_len = len(gold_node_list)

    if gold_len < test_len:
        switch = True
        test_len, gold_len = gold_len, test_len
        test_node_list, gold_node_list = gold_node_list, test_node_list
        gold_tree, test_tree = test_tree, gold_tree

    dis_graph = np.zeros(shape=(test_len, gold_len))

    for i in range(test_len):
        for j in range(gold_len):
            if metric_mode == 1:
                dis = test_node_list[i].distance(gold_node_list[j])
            else:
                dis = get_simple_lca_length(std_tree=std_tree,
                                            test_gold_dict=test_gold_dict,
                                            node1=test_node_list[i],
                                            node2=gold_node_list[j],
                                            switch=switch)

            if dis <= threshold_dis:
                dis_graph[i][j] = -dis
            else:
                dis_graph[i][j] = -0x3f3f3f3f/2

    dis_graph = dis_graph.tolist()
    return dis_graph, switch, test_len, gold_len


class KM:
    def __init__(self, maxn, nx, ny, G):
        self.maxn = 1000
        self.ny = ny
        self.nx = nx
        self.G = G

        self.KM_INF = 0x3f3f3f3f
        self.match = [-1]*maxn
        self.slack = [0]*maxn
        self.visx = [False]*maxn
        self.visy = [False]*maxn
        self.lx = [0]*maxn
        self.ly = [0]*maxn
        self.fa = [0]*(maxn*2)

    def find_path(self, x):
        self.visx[x] = True
        for y in range(self.ny):
            if self.visy[y]:
                continue
            tmp_delta = self.lx[x] + self.ly[y] - self.G[x][y]
            if tmp_delta < EPS:
                self.visy[y] = True
                if self.match[y] == -1 or self.find_path(self.match[y]):
                    self.match[y] = x
                    return True
            elif self.slack[y] > tmp_delta:
                self.slack[y] = tmp_delta
        return False

    def km(self):
        for x in range(self.nx):
            for j in range(self.ny):
                self.slack[j] = self.KM_INF
            while True:
                self.visx = [False] * self.maxn
                self.visy = [False] * self.maxn
                if self.find_path(x):
                    break
                delta = self.KM_INF
                for j in range(self.ny):
                    if not self.visy[j] and delta > self.slack[j]:
                        delta = self.slack[j]
                for i in range(self.nx):
                    if self.visx[i]:
                        self.lx[i] -= delta
                for j in range(self.ny):
                    if self.visy[j]:
                        self.ly[j] += delta
                    else:
                        self.slack[j] -= delta

    def solve(self):
        self.match = [-1]*self.maxn
        self.ly = [0]*self.maxn

        for i in range(self.nx):
            self.lx[i] = -self.KM_INF
            for j in range(self.ny):
                if self.lx[i] < self.G[i][j]:
                    self.lx[i] = self.G[i][j]
        self.km()

    def get_max_dis(self):
        ans = 0.0
        for i in range(0, self.ny):
            if self.match[i] != -1 and self.G[self.match[i]][i] != -self.KM_INF/2:
                ans += self.G[self.match[i]][i]
        return ans

    def print_match(self):
        for i in range(0, self.ny):
            if self.match[i] != -1 and self.G[self.match[i]][i] != -self.KM_INF/2:
                print("gold node: {} test node {}".format(self.match[i], i))


if __name__ == "__main__":
    pass
