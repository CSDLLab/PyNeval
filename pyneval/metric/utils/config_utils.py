DINF = 999999999999.0
EPS = 0.0000001
SAME_POS_TH = 0.03
MIN_SIZE = 0.8
FLOAT_ERROR = 0.001


def get_avg_radius(gold_swc_tree, rate=0.1):
    total_length = gold_swc_tree.length()
    total_node = gold_swc_tree.size()
    if total_node <= 1:
        dis_threshold = 0.1
    else:
        dis_threshold = (total_length/total_node)*rate
    return dis_threshold


def get_screen_output():
    res = {
        "ssd": ["ssd_score", "recall", "precision", "f1_score"],
        "length": ["recall", "precision", "f1_score"],
        "cn": ["mean_dis", "recall", "precision", "f1_score"],
        "diadem": ["diadem_score"],
    }
    return res


def get_default_configs(method):
    configs = dict()
    if method == "ssd":
        configs["threshold_mode"] = 1
        configs["ssd_threshold"] = 2
        configs["up_sample_threshold"] = 2
        configs["scale"] = [1, 1, 1]
        configs["debug"] = False

    if method == "length":
        configs["radius_mode"] = 1
        configs["radius_threshold"] = 2
        configs["length_threshold"] = 0.2
        configs["scale"] = [1, 1, 1]
        configs["debug"] = False

    if method == "diadem":
        configs["weight_mode"] = 1
        configs["remove_spur"] = False
        configs["count_excess_nodes"] = True
        configs["align_tree_by_root"] = False
        configs["list_miss"] = True
        configs["list_distant_matches"] = True
        configs["list_continuations"] = True
        configs["find_proper_root"] = True
        configs["scale"] = [1, 1, 1]
        configs["xy_threshold"] = 2
        configs["z_threshold"] = 1
        configs["default_xy_path_error_threshold"] = 0.05
        configs["default_z_path_error_threshold"] = 0.05
        configs["local_path_error_threshold"] = 0.4
        configs["debug"] = False

    if method == "cn":
        configs["distance_threshold"] = 2
        configs["critical_type"] = 1
        configs["scale"] = [1, 1, 1]
        configs["true_positive"] = 3
        configs["missed"] = 4
        configs["excess"] = 5

    if method == "link":
        configs["scale"] = [1, 1, 1]

    if method == "volume":
        configs["length_threshold"] = 1.0
        configs["intensity_threshold"] = 1.0
        configs["debug"] = False

    return configs


def get_config_schema(method):
    schema = dict()

    if method == "ssd":
        schema = {
            "title": "ssd metric schema",
            "type": "object",
            "required": [
                "threshold_mode",
                "ssd_threshold",
                "up_sample_threshold",
                "scale",
                "debug"
            ],
            "properties": {
                "threshold_mode": {"type": "integer", "enum": [1, 2]},
                "ssd_threshold": {"type": "number", "minimum": 0},
                "up_sample_threshold": {"type": "number", "minimum": 0},
                "scale": {
                    "type": "array",
                    "additionalItems": {"type": "number", "minimum": 0},
                    "minItems": 3,
                    "maxItems": 3
                },
                "debug": {"type": "boolean"}
            }
        }

    if method == "length":
        schema = {
            "title": "length metric schema",
            "type": "object",
            "required": [
                "radius_mode",
                "radius_threshold",
                "length_threshold",
                "scale",
                "debug"
            ],
            "properties": {
                "radius_mode": {"type": "number", "enum": [1,2]},
                "radius_threshold": {"type": "number", "minimum": 0},
                "length_threshold": {"type": "number", "minimum": 0},
                "scale": {
                    "type": "array",
                    "additionalItems": {"type": "number", "minimum": 0},
                    "minItems": 3,
                    "maxItems": 3
                },
                "debug": {"type": "boolean"}
            }
        }

    if method == "diadem":
        schema = {
            "title": "diadem metric schema",
            "type": "object",
            "required": [
                "weight_mode"
            ],
            "properties": {
                "weight_mode": {"type": "number", "enum": [1,2,3,4,5]},
                "remove_spur": {"type": "boolean", "default": "false"},
                "count_excess_nodes": {"type": "boolean", "default": "true"},
                "align_tree_by_root": {"type": "boolean", "default": "false"},
                "list_miss": {"type": "boolean", "default": "false"},
                "list_distant_matches": {"type": "boolean", "default": "false"},
                "list_continuations": {"type": "boolean", "default": "false"},
                "find_proper_root": {"type": "boolean", "default": "true"},
                "scale": {
                    "type":"array",
                    "additionalItems": {"type": "number", "minimum": 0},
                    "minItems": 3,
                    "maxItems": 3
                },
                "xy_threshold": {"type": "number", "minimum": 0},
                "z_threshold": {"type": "number", "minimum": 0},
                "default_xy_path_error_threshold": {"type": "number", "minimum": 0},
                "default_z_path_error_threshold": {"type": "number", "minimum": 0},
                "local_path_error_threshold": {"type": "number", "minimum": 0},
                "debug": {"type": "boolean", "default": "false"}
            }
        }

    if method == "cn":
        schema = {
            "title": "branch metric schema",
            "type": "object",
            "required": [
              "distance_threshold",
              "critical_type",
              "scale",
              "true_positive",
              "missed",
              "excess"
            ],
            "properties": {
                "threshold_dis": {"type": "number", "minimum": 0},
                "threshold_mode": {"type": "number", "enum": [1, 2]},
                "critical_type": {"type": "integer", "enum": [1, 2, 3]},
                "scale": {
                    "type": "array",
                    "additionalItems": {"type": "number", "minimum": 0},
                    "minItems": 3,
                    "maxItems": 3
                },
                "true_positive": {"type": "integer", "exclusiveMinimum": 0},
                "missed": {"type": "integer", "exclusiveMinimum": 0},
                "excess": {"type": "integer", "exclusiveMinimum": 0}
            }
        }

    if method == "link":
        schema = {
            "title": "link metric schema",
            "type": "object",
            "required": [
              "scale"
            ],
            "properties": {
                "scale": {
                    "type": "array",
                    "additionalItems": {"type": "number", "minimum": 0},
                    "minItems": 3,
                    "maxItems": 3
                }
            }
        }

    if method == "volume":
        schema = {
            "title": "length metric schema",
            "type": "object",
            "required": [
              "length_threshold",
              "intensity_threshold",
              "debug"
            ],
            "properties": {
                "length_threshold": {"type": "number", "minimum": 0},
                "intensity_threshold": {"type": "number", "minimum": 0},
                "debug": {"type": "boolean"}
            }
        }

    return schema
