import os


def make_sure_dir_existence(out_dir):
    if out_dir is None:
        return None

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
                return None
    return out_dir


def make_sure_file_end_with(out_path, end_str):
    if out_path is None:
        return None

    while not out_path[-len(end_str):] == end_str:
        print('[Info]: "{}" is not end with {}. Input another path?[y/n]'.format(out_path, end_str))
        choice = input()
        if choice.lower() == 'y':
            print('[Info]: Input new path:')
            out_path = input()
        elif choice.lower() == 'n':
            return None
    return out_path


def make_sure_path_not_exist(out_path):
    if out_path is None:
        return None

    while os.path.exists(out_path):
        print('[Info]: "{}" is already existed. Overwrite?[y/n]'.format(out_path))
        choice = input()
        if choice.lower() == 'y':
            break
        elif choice.lower() == 'n':
            return None
    return out_path


def path_validation(file_path, end_str):
    file_path = os.path.normpath(file_path)
    file_path = make_sure_file_end_with(file_path, end_str)
    if file_path is None:
        return None
    file_dir = os.path.dirname(file_path)
    file_dir = make_sure_dir_existence(file_dir)
    if file_dir is None:
        return None
    file_path = os.path.join(file_dir, os.path.basename(file_path))
    file_path = make_sure_path_not_exist(out_path=file_path)
    return file_path
