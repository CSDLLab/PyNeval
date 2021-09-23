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
    json_file_path = cli_utils.path_validation(json_file_path, ".json")

    if json_file_path is None:
        return False

    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=4)
    return True
