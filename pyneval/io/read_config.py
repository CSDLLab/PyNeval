import os
import platform


def read_int_config(config, config_name, default):
    config_value = 0.0
    if config_name not in config.keys() or config[config_name] == "default":
        print("[Warning: ]config {} is not defined or value is default, default value {} is used".format(
            config_name, default))
        config_value = default
    else:
        config_value = int(config[config_name])
    return config_value


def read_float_config(config, config_name, default):
    config_value = 0.0
    if config_name not in config.keys() or config[config_name] == "default":
        # print("[Warning: ]config {} is not defined or value is default, default value {} is used".format(
        #     config_name, default))
        config_value = default
    else:
        config_value = float(config[config_name])
    return config_value


def read_path_config(config, config_name, default):
    config_value = ""
    if config_name in config:
        config_value = config[config_name]
        if platform.system() == "Linux":
            config_value = '/'.join(config_value.split("\\"))
    else:
        # print("[Warning: ]config {} is not defined, default value {} is used".format(config_name, default))
        config_value = default
    return config_value


def read_bool_config(config, config_name, default):
    config_value = 0.0
    if config_name not in config.keys() or config[config_name] == "default":
        # print("[Warning: ]config {} is not defined or value is default, default value {} is used".format(
        #     config_name, default))
        config_value = default
    else:
        config_value = bool(config[config_name])
    return config_value