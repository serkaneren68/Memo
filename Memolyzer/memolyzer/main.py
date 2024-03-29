from memolyzer.cli import Cli
from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from pandasgui import show

import inspect
def example_def(*args) -> None:
    # chcek args not none
    for arg in args: 
        if type(arg) != list: raise TypeError("Argument can not be {}.".format(type(arg)))

    callers_local_vars = inspect.currentframe().f_back.f_locals.items()

    for ix, item in enumerate(args):
        for var_name, var_val in callers_local_vars:
            if var_val is item:
                print("Bulundu","arg_index:",ix , ", var_name:", var_name, ", var_value:", item)


if __name__ == '__main__':
    args = Cli().get_args()
    print(args)
    map_parser = MapParser(MAP_FILE_PATH)
    map_parser.update_tables(args.modes)


    pd_dfs = list()
    pd_dfs_str = ""

    # exec önerilmiyor çünkü argüman olarak dışarıdan bir string alıyorsun ve bunu değişkene yada koda çeviriyorsun
    # ama pandasgui de df ismi verilen değişkenin ismine eşit
    for mode in args.modes: 
        print(mode)
        exec(f'{mode} = map_parser.tables[mode]') # aynı isimde değişken oluşturuyorum
        exec(f'pd_dfs.append({mode})')

    for i in range(len(args.modes)):
        pd_dfs_str = "pd_dfs[0]" if i == 0 else pd_dfs_str + f", pd_dfs[{i}]"

    if args.show:
        exec(f'gui = show({pd_dfs_str})')

        changed_df = gui.get_dataframes()

        for mode in args.modes:
            exec(f'print("{mode}:",changed_df["{mode}"])')


    # # eğer değişken oluşturulmaz ise pandasgui df ismine untitled veriyor
    # for i in range (len(args.modes)): show(changed_df[f"untitled_{i+1}"])



    # eğer exec kullanmak istemezsek
    pd_idx = []
    for mode in args.modes:
        if mode =="tool_and_invocation":
            tool_and_invocation = map_parser.tables["tool_and_invocation"]
            pd_dfs.append(tool_and_invocation)
            break

        elif mode == "overall":
            overall = map_parser.tables["overall"]
            pd_dfs.append(overall)
            break
            
        elif mode == "link_result":
            link_result = map_parser.tables["link_result"]
            pd_dfs.append(link_result)
            break

        elif mode == "cross_references":
            cross_references = map_parser.tables["cross_references"]
            pd_dfs.append(cross_references)
            break

        elif mode == "locate_result_sections":
            locate_result_sections = map_parser.tables["locate_result_sections"]
            pd_dfs.append(locate_result_sections)
            break

        elif mode == "locate_result_symbols_name":
            locate_result_symbols_name = map_parser.tables["locate_result_symbols_name"]
            pd_dfs.append(locate_result_symbols_name)
            break

        elif mode == "locate_result_symbols_address":
            locate_result_symbols_address = map_parser.tables["locate_result_symbols_address"]
            pd_dfs.append(locate_result_symbols_address)

    