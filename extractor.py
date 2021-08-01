import json, copy, os

class Extractor:

    def __init__(self, config_file="config.json", output_base_dir="./output"):
        if not os.path.isfile(config_file) or not config_file.endswith("config.json"):
                print(config_file.endswith("config.json"))
                raise Exception('Please provide a valid path to a "config.json" file '+
                                'that defines a "template" and an "outputPath". Check config.sample.json for reference.')

        self.config_file = config_file
        self.config = self.load_config()
        self.template = self.config["template"]
        self.flattened_template_keys = []
        self.output = copy.deepcopy(self.template)
        self.output_base_dir = output_base_dir \
                    if not "outputPath" in self.config \
                    else self.get_config("outputPath")
        self.create_flattened_template_keys()

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

    def create_flattened_template_keys(self, template=None, parent_keys=""):   
        if template is None:
            template = self.template
        
        for key in template.keys():
            if type(template[key]) is dict:
                self.create_flattened_template_keys(
                        template[key], parent_keys+key+"."
                    )
            else:
                self.flattened_template_keys.append(parent_keys+key)

    def get_flattened_template_keys(self):
        return self.flattened_template_keys

    def get_template(self):
        return self.template

    def get_output(self, key):
        return self.get_config(key, self.output)

    def set_output(self, flattened_key, data):
        keys = flattened_key.split(".")
        output = self.output
        for key in keys[:-1]:
            output = output[key]
        output[keys[-1]] = data

    def save_output(self):
        output_dir = os.sep.join([
                        self.output_base_dir,
                        self.get_output("localityId"),
                        self.get_output("attractionId")
                    ])

        output_file = os.sep.join([
                        output_dir,
                        self.get_output("reviewId")+".json"
                    ])

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except FileExistsError:
                pass
        
        with open(output_file, "w+") as f:
            json.dump(self.output, f)

        print("File {} created".format(output_file))

    def extract(self):
        pass