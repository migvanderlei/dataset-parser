import os, json

class Configurable:

    def __init__(self, config_file="config.json"):
        if not os.path.isfile(config_file) or not config_file.endswith("config.json"):
                print(config_file.endswith("config.json"))
                raise Exception('Please provide a valid path to a "config.json" file '+
                                'that defines a "template" and an "outputPath". Check config.sample.json for reference.')
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file) as f:
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
