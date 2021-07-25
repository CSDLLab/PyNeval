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
    if not is_json_file(json_file_path):
        raise PyNevalError('[Error: ] " {} "  is not a json file. Wrong format'.format(json_file_path))
    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=4)
        if DEBUG:
            print (type(data))
    return True


if __name__ == "__main__":
    # read_json(r'{"method": 2,"thereshold": "default"')
    test_json = read_json("/home/zhanghan/01_project/Pyneval/config/schemas/branch_metric_schema.json")
    save_json("./test.json", test_json)
