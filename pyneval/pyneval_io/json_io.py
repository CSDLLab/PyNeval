import json
import os

from pyneval.errors.exceptions import PyNevalError
from pyneval.metric.utils import cli_utils


def read_json(json_file_path):
    json_file_path = os.path.normpath(json_file_path)
    with open(json_file_path, "r") as f:
        data = json.load(f)
        return data


def save_json(json_file_path, data):
    if json_file_path is None:
        return False
    if not os.path.exists(os.path.dirname(json_file_path)):
        os.mkdir(os.path.dirname(json_file_path))
    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=4)
    return True
