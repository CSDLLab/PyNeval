import json
import os,sys


def read_json(json_file_path, DEBUG=False):
    json_file_path = os.path.normpath(json_file_path)
    if not os.path.isfile(json_file_path) or not (json_file_path[-5:] == ".json" or json_file_path[-5:] == ".JSON"):
        try:
            data = json.loads(json_file_path)
            if DEBUG:
                print(data)
            return data
        except:
            raise Exception("[Error: ] \" {} \"  is not a json file. Wrong format".format(json_file_path))

    with open(json_file_path,'r') as f:
        data = json.load(f)
        if DEBUG:
            print(type(data))
        return data


def save_json(json_file_path, data, DEBUG=False):
    json_file_path = os.path.normpath(json_file_path)
    if not(json_file_path[-5:] == ".json" or json_file_path[-5:] == ".JSON"):
        raise Exception("[Error: ] \" {} \"  is not a json file. Wrong format".format(json_file_path))
    try:
        with open(json_file_path, 'w') as f:
            json.dump(data, f, indent=4)
            if DEBUG:
                print(type(data))
    except:
        raise Exception("[Error: ] json file save error")
    return True


if __name__ == "__main__":
    # read_json(r'{"method": 2,"thereshold": "default"')
    test_json = read_json("/home/zhanghan/01_project/Pyneval/config/schemas/branch_metric_schema.json")
    save_json("./test.json", test_json)
