import json

class Configurable: 
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
