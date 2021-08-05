import os, json

class Configurable:

    def __init__(self, config_file=None):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if self.config_file is None:
            dir_name = os.path.dirname(__file__)
            file_name = os.path.join(dir_name, '..', 'config', 'config.json')
        else:
            file_name = self.config_file

        with open(file_name) as f:
            return json.load(f)

    def get_config(self, key, config=None):
        if config is None:
            config = self.config

        if "." in key:
            return self.get_config(
                    key[key.find(".")+1:],
                    config[key[:key.find(".")]]
                )
        return config[key]

    def set_config(self, flattened_key, data):
        keys = flattened_key.split(".")
        config = self.config
        for key in keys[:-1]:
            config = config[key]
        config[keys[-1]] = data
