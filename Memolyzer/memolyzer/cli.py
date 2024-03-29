import argparse
from typing import List
from .map_parser import temp_tables

class Cli:
    def __init__(self):
        self.argparser = argparse.ArgumentParser(
            prog="Memolyzer",
            description="Tasking Compiler Compitable Memory Analyzer",
            epilog="Your analysis is done, Thanks for using %(prog)s :) ")
        
        self.argparser.add_argument("--map_path", type=str, required=True, help="path of map file for processing")
        self.argparser.add_argument("--modes", nargs="+", type=str, required=True, 
                                    help=f"Mode Types. Choose ore or more of these options: {list(temp_tables.keys())}.",
                                    choices=list(temp_tables.keys()))
        
        self.argparser.add_argument("--output", nargs="*", choices=["csv","xlsx","json","html"], type=str, default="[]", help="Choose your Output Types Csv, Excel, Json, Html.")
        self.argparser.add_argument('--show', action=argparse.BooleanOptionalAction, help="Show Graphical User Interface")
        self.args = self.argparser.parse_args()

    def get_args(self):
        return self.args