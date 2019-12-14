
dis_threshold = 0.1


def get_default_threshold(gold_swc_tree):
    global dis_threshold
    total_length = gold_swc_tree.length()
    total_node = gold_swc_tree.node_count()
    if total_node <= 1:
        dis_threshold = 0.1
    else:
        dis_threshold = (total_length/total_node)/10