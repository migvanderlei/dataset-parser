import argparse 
from src.dispatcher import Dispatcher
from src.collector import Collector

def main():
    parser = argparse.ArgumentParser(description="Dataset parsing tool")
    parser.add_argument(
        "-i",
        "--input_path",
        help="An absolute path to the HTML files dir like \"/home/user/data/*/*/*.html\""
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help="An absolute path to a directory where output JSON files will be written like \"/home/user/output/\""
    )
    parser.add_argument(
        "--config",
        help="An absolute or relatice path to a JSON configuration file like \"./config/config.json/\""
    )
    parser.add_argument(
        "-e",
        "--extract",
        action="store_true",
        help="Run extraction process"
    )
    parser.add_argument(
        "-c",
        "--collect",
        action="store_true",
        help="Run collection process"
    )

    args = parser.parse_args()

    config_file = args.config
    input_path = args.input_path
    output_path = args.output_path

    if args.extract:
        dispatcher = Dispatcher(config_file=config_file)
        print("Starting extraction process. Check the Dispatcher log file for details: \"{}\"".format(dispatcher.get_log_file("dispatcher")))
        dispatcher.run(input_path)
        print("Extraction process finished.")

    elif args.collect:
        collector = Collector(config_file=config_file)
        print("Starting collection process. Check the collector log file for details: \"{}\"".format(collector.get_log_file("collector")))
        collector.collect()
        print("Collection process finished.")

if __name__ == "__main__":
    main()
