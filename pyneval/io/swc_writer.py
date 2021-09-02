import os


def is_path_valid(file_path):
    tmp_path, tmp_file = os.path.split(file_path)

    if not os.path.exists(file_path):
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        new_file = open(file_path, "w")
        new_file.close()

    # if os.path.isdir(file_path):
    # raise PyNevalError("[Error: ] file: \"{}\" has exist in path: \"{}\". and it is a menu"
    #                 .format(tmp_file, tmp_path))
    # return False

    return not os.path.isdir(file_path)


def save_line_tuple_as_swc(match_fail, file_path):
    with open(file_path, "w") as f:
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
        print ("pos_1: {}, pos_2 {}".format(line_tuple[0]._pos, line_tuple[1]._pos))


def print_swc(object):
    if isinstance(object, set):
        print_line_tuple_swc(object)


def swc_save(swc_tree, out_path, extra=None):
    out_path = os.path.normpath(out_path)
    out_dir = os.path.dirname(out_path)

    while not os.path.exists(out_dir):
        print('[Info]: "{}" dose not exist. Create new path?[y/n]'.format(out_dir))
        choice = input()
        if choice.lower() == 'y':
            os.makedirs(out_dir)
        elif choice.lower() == 'n':
            print('[Info]: "{}" dose not exist. Input new directory?[y/n]'.format(out_dir))
            choice = input()
            if choice.lower() == 'y':
                print('[Info]: Input new directory')
                out_dir = input()
            elif choice.lower() == 'n':
                return False
            else:
                continue
    out_new_path = os.path.join(out_dir, os.path.basename(out_path))
    while not out_new_path[-4:] == '.swc':
        print('[Info]: "{}"  is not a swc file. Input another path?[y/n]'.format(out_new_path))
        choice = input()
        if choice.lower() == 'y':
            print('[Info]: Input new path:')
            out_new_path = input()
        elif choice.lower() == 'n':
            return False

    while os.path.exists(out_new_path):
        print('[Info]: "{}" is already existed. Overwrite?[y/n]'.format(out_new_path))
        choice = input()
        if choice.lower() == 'y':
            break
        elif choice.lower() == 'n':
            return False

    swc_node_list = swc_tree.get_node_list()
    swc_tree.sort_node_list(key="id")
    with open(out_new_path, "w") as f:
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