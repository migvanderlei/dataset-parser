from src.configurable import Configurable
import copy

class ReviewFormatter(Configurable):

    def __init__(self, aggregated_output, unique_keys=[], keys=[], config_file=None):
        Configurable.__init__(self, config_file)

        self.aggregated_output = aggregated_output
        self.unique_template_keys = unique_keys
        self.template_keys = keys
        self.multi_keys = [x for x in keys if x not in set(unique_keys)]
        self.output_count = 0
        self.output = []
        self.check_integrity()
    
    def get_output(self, key, i=0):
        return self.get_config(key, self.output[i])

    def set_output(self, flattened_key, data, i=0):
        keys = flattened_key.split(".")
        output = self.output[i]
        for key in keys[:-1]:
            output = output[key]
        output[keys[-1]] = data

    def check_integrity(self):
        keys_count = []
        failed = False
        output_count = 0
        for key in self.multi_keys:
            count = len(self.aggregated_output[key])
            if count > 0 and output_count == 0:
                output_count = count
            if output_count != count:
                failed = True
            keys_count.append({key:count})

        if failed:
            raise Exception("Integrity check failed. Output count does not match for all keys: %s." % (keys_count))

        self.output_count = output_count
        return True

    def format_reviews(self):
        for i in range(self.output_count):
            self.output.append(copy.deepcopy(self.aggregated_output))
            for key in self.multi_keys:
                self.set_output(
                    key, self.aggregated_output[key][i], i
                )
        return self.output
