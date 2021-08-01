import json, copy, os
from configurable import Configurable

class Extractor(Configurable):

    def __init__(self, input_file, config_file="config.json", output_base_dir="./output"):
        Configurable.__init__(self, config_file)

        self.input_file = input_file
        self.input = None
        self.template = self.config["template"]
        self.flattened_template_keys = []
        self.output = copy.deepcopy(self.template)
        self.output_base_dir = output_base_dir \
                    if not "outputPath" in self.config \
                    else self.get_config("outputPath")
        self.create_flattened_template_keys()
        self.load_input()

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

    def load_input(self):
        if self.input is None:
            with open(self.input_file, "r") as f:
                self.input = f.read()

    def extract(self):
        pass
