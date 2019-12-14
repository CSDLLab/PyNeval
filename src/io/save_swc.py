import os


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
        f.write("# total unmatched edges: {}".format(len(match_fail)))
        for line_tuple in match_fail:
            print("??")
            f.write("{} {} {} {} {} {} {}\n".format(line_tuple[0].get_id(),
                                                  line_tuple[0]._type,
                                                  line_tuple[0]._pos[0],
                                                  line_tuple[0]._pos[1],
                                                  line_tuple[0]._pos[2],
                                                  line_tuple[0].radius(),
                                                  line_tuple[0].parent.get_id()))
            f.write("{} {} {} {} {} {} {}\n".format(line_tuple[1].get_id(),
                                                  line_tuple[1]._type,
                                                  line_tuple[1]._pos[0],
                                                  line_tuple[1]._pos[1],
                                                  line_tuple[1]._pos[2],
                                                  line_tuple[1].radius(),
                                                  line_tuple[1].parent.get_id()))
        f.write("# --End--")

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

if __name__ == "__main__":
    # os.makedirs("a/b/c")
    save_as_swc(None, "a/b/c")