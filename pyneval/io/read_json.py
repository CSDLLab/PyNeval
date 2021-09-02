import json
import os
import sys

from pyneval.errors.exceptions import PyNevalError


def is_json_file(json_file):
    return json_file[-5:] in (".json", ".JSON")


def read_json(json_file_path, DEBUG=False):
    json_file_path = os.path.normpath(json_file_path)
    with open(json_file_path, "r") as f:
        data = json.load(f)
        if DEBUG:
            print (type(data))
        return data


def save_json(json_file_path, data, DEBUG=False):
    json_file_path = os.path.normpath(json_file_path)
    json_file_dir = os.path.dirname(json_file_path)
    while not os.path.exists(json_file_dir):
        print('[Info]: "{}" dose not exist. Create new path?[y/n]'.format(json_file_dir))
        choice = input()
        if choice.lower() == 'y':
            os.makedirs(json_file_dir)
        elif choice.lower() == 'n':
            print('[Info]: "{}" dose not exist. Input new directory?[y/n]'.format(json_file_dir))
            choice = input()
            if choice.lower() == 'y':
                print('[Info]: Input new directory')
                json_file_dir = input()
            elif choice.lower() == 'n':
                return False
            else:
                continue
    json_file_new_path = os.path.join(json_file_dir, os.path.basename(json_file_path))
    while not is_json_file(json_file_new_path):
        print('[Info]: "{}"  is not a json file. Input another path?[y/n]'.format(json_file_new_path))
        choice = input()
        if choice.lower() == 'y':
            print('[Info]: Input new path:')
            json_file_new_path = input()
        elif choice.lower() == 'n':
            return False

    while os.path.exists(json_file_new_path):
        print('[Info]: "{}" is already existed. Overwrite?[y/n]'.format(json_file_new_path))
        choice = input()
        if choice.lower() == 'y':
            break
        elif choice.lower() == 'n':
            return False

    with open(json_file_new_path, "w") as f:
        json.dump(data, f, indent=4)
        if DEBUG:
            print(type(data))
    return True
