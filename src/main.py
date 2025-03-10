import argparse
import ROOT
import logging

import find_json
import find_newest
import find_range
import histograms
import produce_ratio
import produce_responses
import produce_time_evolution
import produce_vetomaps
from plotting import produce_plots
import skim

class ProcessingState:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='JEC4PROMPT Toolkit: \
            https://github.com/toicca/dijet_rdf/tree/main')
        self.subparsers = self.parser.add_subparsers(dest='subparser_name')
        self.parser.add_argument('--log', type=str, default='INFO', help='Logging level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.args = None
        self.valfuncs = {}
        self.commands = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def init_state(self):
        self.logger.info("Initializing state")
        skim.update_state(self)
        histograms.update_state(self)
        # histograms.add_hist_parser(self.subparsers)
        # find_json.add_find_json_parser(self.subparsers)
        # find_newest.add_find_newest_parser(self.subparsers)
        # find_range.add_find_range_parser(self.subparsers)
        # produce_plots.add_plots_parser(self.subparsers)
        # produce_vetomaps.add_vetomaps_parser(self.subparsers)
        
        self.args = self.parser.parse_args()
        self.logger.info(f"Parsed arguments: {self.args}")
        self.logger.info(f"Subparser name: {self.args.subparser_name}")
        self.logger.info(f"Logging level: {self.args.log}")
        self.logger.setLevel(self.args.log)
        self.valfuncs[self.args.subparser_name](self.args)

    def execute_command(self):
        self.logger.info(f"Executing command: {self.args.subparser_name}")
        self.commands[self.args.subparser_name](self)

if __name__ == "__main__":
    state = ProcessingState()
    state.init_state()
    state.execute_command()