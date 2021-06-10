from pyneval.io.read_json import read_json


def get_detail_type(metric_name):
    detail_type_annotation = dict()
    detail_type_annotation["ssd_metric"] = "# 1: gold standard root\n" \
                                           "# 2: gold standard branch(degree >= 3)\n" \
                                           "# 3: gold standard continuation(degree == 2)\n" \
                                           "# 4: gold standard leaf(degree == 1)\n" \
                                           "# 5: reconstruction root\n" \
                                           "# 6: reconstruction branch(degree >= 3)\n" \
                                           "# 7: reconstruction continuation(degree == 2)\n" \
                                           "# 8: reconstruction leaf(degree == 1)\n" \
                                           "# 9: mismatched node(regardless rules above)\n\n"
    detail_type_annotation["length_metric"] = "# 1: gold standard root\n" \
                                              "# 2: gold standard branch(degree >= 3)\n" \
                                              "# 3: gold standard continuation(degree == 2)\n" \
                                              "# 4: gold standard leaf(degree == 1)\n" \
                                              "# 5: reconstruction root\n" \
                                              "# 6: reconstruction branch(degree >= 3)\n" \
                                              "# 7: reconstruction continuation(degree == 2)\n" \
                                              "# 8: reconstruction leaf(degree == 1)\n" \
                                              "# 9: edge between this node and its parent is mismatched" \
                                              "(regardless rules above)\n\n"
    detail_type_annotation["branch_metric"] = "# type of nodes in this metric detail could be change in configs\n" \
                                              "# true_positive_type: successfully reconstructed nodes, " \
                                              "exists in both GS and R\n" \
                                              "# missed: wrongly reconstructed as negative. " \
                                              "exist in GS but not in R\n" \
                                              "# excess: wrongly reconstructed as positive. " \
                                              "exist in R but not in GS.\n\n"
    detail_type_annotation["diadem_metric"] = "# 1: gold standard root\n" \
                                              "# 2: gold standard branch(degree >= 3)\n" \
                                              "# 3: gold standard continuation(degree == 2)\n" \
                                              "# 4: gold standard leaf(degree == 1)\n" \
                                              "# 5: reconstruction root\n" \
                                              "# 6: reconstruction branch(degree >= 3)\n" \
                                              "# 7: reconstruction continuation(degree == 2)\n" \
                                              "# 8: reconstruction leaf(degree == 1)\n" \
                                              "# 9: missed: exist in GS but not in R\n" \
                                              "# 10 excess: exist in R but not in GS\n\n"
    if metric_name not in detail_type_annotation:
        return None
    return detail_type_annotation[metric_name]


if __name__ == "__main__":
    print(get_detail_type("branch_metric"))