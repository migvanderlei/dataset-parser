import logging
from datetime import datetime
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from glob import glob
from src.configurable import Configurable
from src.extractor import Extractor

class Dispatcher(Configurable):
    def __init__(self, config_file=None):
        Configurable.__init__(self, config_file)
        logging.basicConfig(format="%(asctime)s: [%(levelname)s] %(message)s", level=logging.INFO,
                            datefmt="%H:%M:%S", filename=self.get_log_file('dispatcher'))
        max_process_count = self.get_config("maxProcessCount")

        if max_process_count:
            if type(max_process_count) == int:
                if max_process_count > multiprocessing.cpu_count():
                    raise Exception("The maxProcessCount parameter should be less or equal the number of available CPU cores.")
                self.max_process_count = max_process_count
            elif type(max_process_count) == float:
                self.max_process_count = int(multiprocessing.cpu_count() * max_process_count)
        else:
            logging.warning("maxProcessCount parameter not found. Setting the maximum process number to 30% of the CPU cores.")
            self.max_process_count = int(multiprocessing.cpu_count() * 0.3)


    def load_inputs(self, input_path):
        return glob(input_path)


    def run(self, input_path=None):
        if not input_path:
            input_path = self.config["inputPath"]

        input_list = self.load_inputs(input_path)

        logging.info("Found %d files to process." % len(input_list))
        success_count = 0
        error_count = 0

        with ProcessPoolExecutor(max_workers=self.max_process_count) as executor:
            logging.info("Starting extraction process with {} parallel processess.".format(self.max_process_count))

            start_time = datetime.now()
            for result in executor.map(handle_extraction, input_list, [self.config_file] * len(input_list)):
                failed, message, _, _, _, input_file = result
                if failed:
                    logging.error("{} File: \"{}\"".format(message, input_file))
                    error_count += 1
                else: 
                    logging.info("{} File: \"{}\"".format(message, input_file))
                    success_count += 1

            elapsed_time = datetime.now() - start_time
            logging.info("Extraction process finished in {}.".format((elapsed_time)))
            logging.info("Extracted {} successfully ({:.2f}%). Found {} errors ({:.2f}%)."
                        .format(success_count, success_count / len(input_list) * 100, error_count, error_count / len(input_list) * 100))

def handle_extraction(input_file, config_file=None):
    e = Extractor(input_file, config_file)
    return e.extract()
