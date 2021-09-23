import os
from pyneval.metric.utils import cli_utils


def swc_save(swc_tree, out_path, extra=None):
    out_path = cli_utils.path_validation(out_path, ".swc")

    if out_path is None:
        return False

    swc_node_list = swc_tree.get_node_list()
    swc_tree.sort_node_list(key="compress")
    with open(out_path, "w") as f:
        f.truncate()
        if extra is not None:
            f.write(extra)
        for node in swc_node_list:
            if node.is_virtual():
                continue
            try:
                f.write(
                    "{} {} {} {} {} {} {}\n".format(
                        node.get_id(),
                        node._type,
                        node.get_x(),
                        node.get_y(),
                        node.get_z(),
                        node.radius(),
                        node.parent.get_id(),
                    )
                )
            except:
                continue
    return True
