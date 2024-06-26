import argparse
from typing import List
from .map_parser import temp_tables, MAP_FILE_PATH
from .modes import temp_modes

class Cli:
    def __init__(self):
        self.argparser = argparse.ArgumentParser(
            prog="Memolyzer",
            description="Tasking Compiler Compitable Memory Analyzer",
            epilog="Your analysis is done, Thanks for using %(prog)s :) ")

        self.argparser.add_argument("--map_path", type=str, required=True, help="path of map file for processing", default=MAP_FILE_PATH)
        self.argparser.add_argument("--modes", nargs="+", type=str, required=True, 
                                    help=f"Mode Types. Choose ore or more of these options: {list(temp_modes.keys())}.",
                                    choices=list(temp_modes.keys()))

        self.argparser.add_argument("-- ", nargs="*", choices=["csv", "xlsx", "json", "html"], type=str, default="[]", help="Choose your Output Types Csv, Excel, Json, Html.")
        self.argparser.add_argument("--config_type", nargs="1", choices=["xlsx", "json"], type=str, default="json", help="Choose your Config Type. Excel or Json.")
        self.argparser.add_argument('--show', action=argparse.BooleanOptionalAction, help="Show Graphical User Interface")
        self.argparser.add_argument('--interactive', action=argparse.BooleanOptionalAction, help="Interactive Mode")
        self.args = self.argparser.parse_args()

    def get_args(self):
        return self.args