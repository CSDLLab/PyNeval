from pyneval.metric.utils import config_utils


def get_simple_lca_length(std_tree, test_gold_dict, node1, node2):
    """
    get the corresponding node of node1 and node2 on std tree.
    calculate the lca distance between them
    Exception:
        Exception("[Error: ] std has not been lca initialized yet")
        std tree need to be initialized before running this function
        example:
            std_tree.get_lca_preprocess()
    """
    if std_tree.depth_array is None:
        raise Exception("[Error: ] std has not been lca initialized yet")
    std_id_node_dict = std_tree.get_id_node_dict()

    tmp_node1 = node1
    tmp_node2 = test_gold_dict[node2]

    if tmp_node2 is None:
        raise Exception("[Error: ]Can not find the corresponding node in std tree. ")

    lca_id = std_tree.get_lca(tmp_node1.get_id(), tmp_node2.get_id())
    if lca_id == -1:
        return config_utils.DINF
    lca_node = std_id_node_dict[lca_id]
    return tmp_node1.root_length + tmp_node2.root_length - 2 * lca_node.root_length


class AugmentPath():
    def __init__(self, n_num, m_num):
        self.n_num = n_num
        self.m_num = m_num
        assert(0 <= self.n_num and 0 <= self.m_num)
        self.pa = [-1] * self.n_num
        self.pb = [-1] * self.m_num
        self.vis = [0] * self.n_num
        self.dfn = 0
        self.res = 0
        self.g = []
        for i in range(self.n_num):
            self.g.append([])

    def add(self, src, to):
        assert (0 <= src < self.n_num and 0 <= to < self.m_num)
        self.g[src].append(to)

    def dfs(self, v):
        self.vis[v] = self.dfn
        for u in self.g[v]:
            if self.pb[u] == -1:
                self.pb[u] = v
                self.pa[v] = u
                return True
        for u in self.g[v]:
            if self.vis[self.pb[u]] != self.dfn and self.dfs(self.pb[u]):
                self.pa[v] = u
                self.pb[u] = v
                return True
        return False

    def solve(self):
        while True:
            self.dfn += 1
            cnt = 0
            for i in range(self.n_num):
                if self.pa[i] == -1 and self.dfs(i):
                    cnt += 1
            if cnt == 0:
                break
            self.res += cnt
        return self.res
