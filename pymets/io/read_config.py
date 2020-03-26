import os,platform


def read_float_config(config, config_name, default):
    config_value = 0.0
    if config_name not in config.keys() or config[config_name] == "default":
        config_value = default
    else:
        try:
            config_value = float(config[config_name])
        except:
            raise Exception("[Error: ] Read config info threshold {}. suppose to be a float or \"default\"")
    return config_value


def read_path_config(config, config_name, abs_dir, default):
    config_value = ""
    if config_name in config.keys():
        config_value = config[config_name]
        if platform.system() == "Linux":
            config_value = '/'.join(config_value.split("\\"))
        config_value = os.path.join(abs_dir, config_value)
        if os.path.exists(config_value):
            os.remove(config_value)
    else:
        config_value = default
    return config_value
