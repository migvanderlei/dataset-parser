import os
import json
import logging
from pandas import json_normalize
from src.configurable import Configurable
from datetime import datetime
from glob import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

class Collector(Configurable):

    def __init__(self, input_path=None, output_file="collected-{}.csv", config_file=None, output_base_dir="./generated"):
        Configurable.__init__(self, config_file)
        logging.basicConfig(format="%(asctime)s: [%(levelname)s] %(message)s", level=logging.INFO,
                            datefmt="%H:%M:%S", filename=self.get_log_file('collector'))

        if input_path is None:
            self.input_path = self.config.get("outputPath")
        else:
            self.input_path = input_path
        self.output_file = output_file.format(self.get_timestamp())
        max_threads = self.config.get("maxThreadCount")
        self.max_threads = max_threads if max_threads is not None else 50
        self.output_file_path = self.get_output_file_path(output_base_dir, self.output_file)
        self.csv_headers = []
        self.create_csv_headers_from_keys()

    def create_csv_headers_from_keys(self, template=None, parent_keys=""):   
        if template is None:
            template = self.config["template"]
        
        for key in template.keys():
            if type(template[key]) is dict:
                self.create_csv_headers_from_keys(
                        template[key], parent_keys+key+"_"
                    )
            else: 
                self.csv_headers.append(parent_keys+key)

    def get_output_file_path(self, base_dir, output_file):
        if base_dir.startswith(os.sep):
            file_name = os.path.join(base_dir, output_file)
        else:
            dir_name = os.path.dirname(__file__)
            base_dir = os.path.join(dir_name, "..", base_dir)
            file_name = os.path.join(base_dir, output_file)
        file_name = os.path.abspath(file_name)
        if not os.path.exists(base_dir):
            try:
                os.makedirs(base_dir)
            except FileExistsError:
                pass
        return file_name

    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def get_files_to_collect(self):
        if "*" in self.input_path:
            files = glob(self.input_path)
        else:
            files = glob(self.input_path + "/*/*/*.json")

        if len(files) > 0:
            return files
        else:
            message = "No files found in {}".format(self.input_path)
            logging.error(message)
            raise Exception(message)

    def collect_file(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    def save_collected_json(self, data):
        json_file_name = self.output_file_path.replace(".csv", ".json")
        with open(json_file_name, "w+") as f:
            f.write(json.dumps(data))
        logging.info("JSON file created at \"{}\".".format((json_file_name)))

    def save_json_to_csv(self, data):
        dataframe = json_normalize(data)
        dataframe.to_csv(self.output_file_path, index=False)
        logging.info("CSV file created at \"{}\".".format((self.output_file_path)))


    def collect(self):
        files_to_collect = self.get_files_to_collect()

        logging.info("Found %d files to process." % len(files_to_collect))

        with ThreadPoolExecutor(max_workers=50) as executor:
            logging.info("Starting collection process with {} parallel threads.".format(self.max_threads))

            start_time = datetime.now()
            futures = []
            collected_lines = []
            for file_path in files_to_collect:
                futures.append(executor.submit(self.collect_file, file_path))
            for future in as_completed(futures):
                collected_lines.append(future.result())

            self.save_collected_json(collected_lines)
            self.save_json_to_csv(collected_lines)           

            elapsed_time = datetime.now() - start_time
            logging.info("Collection process finished in {}.".format((elapsed_time)))
