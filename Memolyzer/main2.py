from memolyzer.cli import Cli
from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from memolyzer.table import MapFileTable
from memolyzer.modes import Modes
from pandasgui import show
import datetime

if __name__ == '__main__':
    args = Cli().get_args()
    if args.interactive:
        show()
    modes = Modes(args.modes)
    df = modes.run_modes()

    if args.show:
        show(df)
    
    if not args.output == "[]":
        MapFileTable().save_df_as(df, name=args.modes[0] + datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
