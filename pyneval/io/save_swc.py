import os
from anytree import PreOrderIter


def is_path_valid(file_path):
    tmp_path, tmp_file = os.path.split(file_path)

    if not os.path.exists(file_path):
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        newfile = open(file_path, 'w')
        newfile.close()

    if os.path.isdir(file_path):
        raise Exception("[Error: ] file: \"{}\" has exist in path: \"{}\". and it is a menu"
                        .format(tmp_file, tmp_path))
        return False

    return True


def save_line_tuple_as_swc(match_fail, file_path):
    with open(file_path, 'w') as f:
        f.truncate()
        f.write("# total unmatched edges: {}\n".format(len(match_fail)))
        for line_tuple in match_fail:
            f.write(line_tuple[0].to_swc_str())
        f.write("# --End--\n")


def save_as_swc(object, file_path):
    if not is_path_valid(file_path):
        return False

    if isinstance(object, set):
        save_line_tuple_as_swc(object, file_path)


def print_line_tuple_swc(match_fail_set):
    for line_tuple in match_fail_set:
        print("pos_1: {}, pos_2 {}".format(line_tuple[0]._pos, line_tuple[1]._pos))


def print_swc(object):
    if isinstance(object, set):
        print_line_tuple_swc(object)


def swc_save(swc_tree, out_path):
    if not is_path_valid(out_path):
        return False
    swc_node_list = swc_tree.get_node_list()
    swc_tree.sort_node_list(key="id")
    with open(out_path, 'w') as f:
        f.truncate()
        for node in swc_node_list:
            if node.is_virtual():
                continue
            try:
                f.write("{} {} {} {} {} {} {}\n".format(
                    node.get_id(), node._type, node.get_x(), node.get_y(), node.get_z(), node.radius(), node.parent.get_id()
                ))
            except:
                continue
