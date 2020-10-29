DINF = 999999999999.0
EPS = 0.0000001
SAME_POS_TH = 0.03


def get_default_threshold(gold_swc_tree):
    total_length = gold_swc_tree.length()
    total_node = gold_swc_tree.size()
    if total_node <= 1:
        dis_threshold = 0.1
    else:
        dis_threshold = (total_length/total_node)/10
    print("reshold = ", dis_threshold)
    return dis_threshold
