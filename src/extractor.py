import json, copy, os, re
from src.configurable import Configurable
from src.review_formatter import ReviewFormatter

class Extractor(Configurable):

    def __init__(self, input_file, config_file=None, output_base_dir="./output"):
        Configurable.__init__(self, config_file)

        self.input_file = input_file
        self.input = None
        self.required_keys = self.get_config("requiredTemplateKeys")
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
                # to match uniqueTemplateKeys when a given key is nested
                unique_keys = self.get_config("uniqueTemplateKeys")
                for unique_key in unique_keys:
                    if unique_key in parent_keys+key and not unique_key == parent_keys+key:
                        unique_keys.append(parent_keys+key)
                        self.set_config("uniqueTemplateKeys", unique_keys)

    def get_flattened_template_keys(self):
        return self.flattened_template_keys

    def get_template(self):
        return self.template

    def get_template_regex(self, key):
        return self.get_config(key, self.template)
    
    def get_output(self, key, output=None):
        if not output:
            output = self.output
        return self.get_config(key, output)

    def set_output(self, flattened_key, data, output=None):
        if not output:
            main_output = self.output

        keys = flattened_key.split(".")
        output = main_output
        for key in keys[:-1]:
            output = output[key]
        output[keys[-1]] = data

    def save_output(self, output):
        locality_id = self.get_output("localityId", output)
        attraction_id = self.get_output("attractionId", output)
        review_id = self.get_output("reviewId", output)

        if locality_id and attraction_id and review_id:
            output_dir = os.sep.join([
                            self.output_base_dir,
                            locality_id,
                            attraction_id
                        ])

            output_file = os.sep.join([
                            output_dir,
                            review_id+".json"
                        ])

            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except FileExistsError:
                    pass

            with open(output_file, "w+") as f:
                json.dump(output, f)
            
            return output_file
        else:
            raise Exception("Cannot save output file properly because one of those is empty: {}".format({
                "localityId": locality_id,
                "attractionId": attraction_id,
                "reviewId": attraction_id
            }))

    def load_input(self):
        if self.input is None:
            try:
                with open(self.input_file, "r") as f:
                    self.input = f.read()
                if "charsToPurge" in self.config and len(self.get_config("charsToPurge")) > 0:
                    for c in self.get_config("charsToPurge"):
                        self.input = self.input.replace(c, "")

            except Exception as e:
                raise Exception("A problem ocurred while reading the input file: {}. Please input only absolute paths.".format(e))

    def extract(self):
        failed_keys = []
        success_keys = []
        output_files = []
        input_file = self.input_file
        message = "Extracted {} keys successfully with {} failing keys."
        failed = False

        template_keys = self.get_flattened_template_keys()
        incomplete_data = False

        for key in template_keys:
            try:
                template_regex = self.get_template_regex(key)

                extracted_data = re.findall(template_regex, self.input)
                if len(extracted_data) > 10:
                    extracted_data = extracted_data[:10]

                if len(extracted_data) > 0:
                    if key in self.get_config("uniqueTemplateKeys"):
                        self.set_output(key, extracted_data[0])
                    else:
                        self.set_output(key, extracted_data)
                    success_keys.append(key)
                else:
                    if key in self.required_keys:
                        self.set_output(key, "")
                        failed_keys.append(key)
                        incomplete_data = True
                        failed = True
                    else:
                        self.set_output(key, "None")
                
            except Exception as e:
                message += "An exception ocurred: {}.".format(e)
                failed = True

        if incomplete_data:
            failed = True
            message = "Review is being discarded for having missing data for: {}.".format(failed_keys)
            return (failed, message, success_keys, failed_keys, output_files, input_file)
        else:
            message = message.format(len(success_keys), len(failed_keys))

        try:
            formatter = ReviewFormatter(
                self.output, self.get_config("uniqueTemplateKeys"),
                self.flattened_template_keys, self.config_file
            )
            formatted_reviews = formatter.format_reviews()
            for review in formatted_reviews:
                output_files.append(
                    self.save_output(review)
                )

        except Exception as e:
            failed = True
            message = "An error occurred, discarding review. The exception was: {}.".format(e)
            success_keys = []
            failed_keys = []
            output_files = []

        return (failed, message, success_keys, failed_keys, output_files, input_file)
