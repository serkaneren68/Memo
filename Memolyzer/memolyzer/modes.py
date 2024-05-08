from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from memolyzer.table import MapFileTable
from pandasgui import show
import pandas as pd
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings("ignore")


class ColorStruct:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_message(message_type:str, text:str, limit_lines:bool=False):

    current_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    # color_map = {
    #     "warning": ColorStruct.WARNING + f"{current_time} : "+ "WARNING !\n",
    #     "error": ColorStruct.ERROR + f"{current_time} : "+ "ERROR !!!\n",
    #     "ok": ColorStruct.GREEN + f"{current_time} : "+ "SUCCEEDED\n",
    # }
    color_map = {
        "warning": ColorStruct.WARNING + "WARNING !:\t",
        "error": ColorStruct.ERROR + "ERROR !!!:\t",
        "ok": ColorStruct.GREEN + "SUCCEEDED.\t",
    }

    if not limit_lines:
        print(f"{color_map[message_type.lower()]}{text}{ColorStruct.RESET}")
    else:
        # 20 ye kadar kısalt,
        if len(text.split("\n")) > 20:
            truncated_text = "\n".join(text.split("\n")[:20])
            print(f"{color_map[message_type.lower()]}{truncated_text}\n...{ColorStruct.RESET}")
        else:
            print(f"{color_map[message_type.lower()]}{text}{ColorStruct.RESET}")



temp_modes = {"symbol_info":None,
              "file_info": None,
              "overall": None,
              "specific_mem_usage": None,
              "mem_section_with_check": None,
              "get_table_from_map_file": None
              }
 
class Modes():
    # def __init__(self, args) -> None:
    #     self.args = args
    #     self.map_parser = MapParser(self.args.map_path)
    def __init__(self) -> None:
        self.map_parser = MapParser(MAP_FILE_PATH)
        self.modes = temp_modes
        
    def run_modes(self):
 
        # yeni mode olacak tool and invocation tablosundan bsw, apsw ve integration olup olmadığı alınacak.
        # (test_map_parser.py daki test_get_tool_and_invocation kullanılabilir.) 
        # ardından processed filesdan bunlar check edilecek eğer arşiv dosyası ise içindeki dosyalar da tek tek bakılacak
        # ardından dosyalar ve her dosya için chipler ve size lar grouplanıp 
        # tek bir df şeklinde chip leri ve size larına göre ne kadar kullanılıp kullanılmadığı bulunacak.
        mode_functions = {"symbol_info":self.get_symbol_info, # tamamlandı
                          "overall": self.get_overall, # percentage yazdırılacak
                          "specific_mem_usage": self.get_specific_mem_usage, # tek bir satırı döndürecek mesela dsrame göre
 
                          # test_mode_5 kullan
                          # excelin her satırı için passed yada failed
                          # eğer ki satır failse (expected içerisinde olmayan sembol, memory e.g. dsram1, ama bu expected da yok şeklinde string döndürecek)
                          "mem_section_with_check": self.get_mem_section_check,  # excel den birden fazla alacak
 
                          # test_mode_5 kullan
                          "file_info": self.get_file_info, # section, Referenced in çıkar, symbol gelicek size tablosu
                          # sorted on symbols de ara symbolu bul, size ve address yazdır
 
                          "get_table_from_map_file": self.get_table_from_map_file,
                          "get_layers_mem_usage": self.get_layers_mem_usage,
                          }
        
        if self.args.modes == ["all"]:
            for key in list(mode_functions.keys()):
                self.modes[key] = mode_functions[key]()
            return
            
        for key in self.args.modes:
            if key in list(mode_functions.keys()):
                self.modes[key] = mode_functions[key]()
            else:
                print(f"Invalid key '{key}'.")

    def get_layers_mem_usage(self):
        file_type_df = self.map_parser.get_file_type(type_and_search_key = { 'Bsw': "thirdPartyObj", 'Integration': "IntegrationLayer", 'Apsw': "Apsw" })
        self.map_parser.init_tables(["processed_files"])
        processed_files_df = self.map_parser.tables["processed_files"][["File", "From archive"]]
        arch_files = file_type_df[file_type_df["File"].str.endswith(".a")]

        merged_df = pd.merge(processed_files_df, file_type_df, on='File', how='left')
        merged_df["Type"] = merged_df["Type"].fillna("Unknown Archive")
        merged_df["Type"] = merged_df.apply(lambda x: arch_files[arch_files["File"] == x["From archive"]]["Type"].values[0]
                                            if x["From archive"] in arch_files["File"].values
                                            else x["Type"], axis=1)

        layers_df = pd.DataFrame(columns=["Type", "Chip", "Size"])
        # get file info for each file
        for file_name in merged_df["File"]:
            file_info_df = self.get_file_info(file_name)
            grouped_file_info_df = file_info_df.groupby("Chip")
            # nan value lar zaten gruplanmıyor
            for chip in grouped_file_info_df.groups.keys():
                size = grouped_file_info_df.get_group(chip)["Size (MAU)"].apply(lambda x: int(x, 16)).sum()
                layers_df = pd.concat([layers_df, pd.DataFrame([[merged_df[merged_df["File"] == file_name]["Type"].values[0], chip, size]], columns=["Type", "Chip", "Size"])], ignore_index=True)
        layers_df = layers_df.groupby(["Type", "Chip"]).sum()
        layers_df = layers_df.reset_index()
        show(layers_df)

    def get_mem_section_check(self):
        excel_df = pd.read_excel("mode5_config.xlsx") # has Type	File Name	Expected Memory (Chip) columns expected memory can be multiple like mpe:dsram1, mpe:dsram2
        # read file names from excel and use get_file_info for each file
        for file_name in excel_df["File Name"]:
            file_info_df = self.get_file_info(file_name)
            file_info_df = file_info_df.dropna()
            grouped_file_info_df = file_info_df.groupby("Chip")

            expected_memory = excel_df[excel_df["File Name"] == file_name]["Expected Memory"].values[0].split(",")
            expected_memory = [mem.strip() for mem in expected_memory]
            for chip in grouped_file_info_df.groups.keys():
                if chip in expected_memory:
                    print_message("ok", f"In {file_name} file, {chip} is in the expected memory list")
                else:
                    print_message("warning", f"In {file_name} file, {chip} is not in the expected memory list. Expected memory list: {expected_memory}")
                    # print_message("warning", f"Memory list in the file: {grouped_file_info_df.get_group(chip)['Chip'].unique().tolist()}")


    def get_file_info(self, file_name:str):
        link_result_df = self.map_parser.get_link_result_by_file_name(file_name)
        if link_result_df.empty:
            print_message("error","Give a valid file_name")
            raise ValueError
        link_result_df_for_sec = link_result_df[['[in] Section', '[out] Section']]
        link_result_df_for_sec["in_out_is_equal"] = link_result_df_for_sec['[in] Section'] == link_result_df_for_sec['[out] Section']
        not_equals_table = link_result_df_for_sec[~link_result_df_for_sec["in_out_is_equal"]]

        self.map_parser.init_tables(["locate_result_sections", "locate_result_combined_sections", "locate_result_symbols_address"])
        locate_result_sections_df = self.map_parser.tables["locate_result_sections"][['Chip', 'Section', 'Size (MAU)', 'Space addr']]
        locate_result_sections_df_renamed = locate_result_sections_df.rename(columns={"Section" : "[out] Section"})
        locate_result_combined_sections_df = self.map_parser.tables["locate_result_combined_sections"]
        symbols_df = self.map_parser.tables["locate_result_symbols_address"][["Name", "Space addr"]]

        if not not_equals_table.empty:
            link_result_df_for_sec = link_result_df_for_sec.drop(not_equals_table.index)
            print_message("warning", f"In {file_name} file, there is conflicts in this sections:\n" + not_equals_table.to_string(), True)
            not_equal_link_res_sec = pd.merge(not_equals_table, locate_result_sections_df_renamed, on='[out] Section', how='left')
            search_on_combined_for_not_equal = not_equal_link_res_sec[not_equal_link_res_sec["Chip"].isna()]
            if not search_on_combined_for_not_equal.empty:
                search_on_combined_for_not_equal = search_on_combined_for_not_equal.drop(columns=["[in] Section"])
                search_on_combined_for_not_equal = search_on_combined_for_not_equal.rename(columns={"[out] Section" : "[in] Section"})
                search_on_combined_for_not_equal = search_on_combined_for_not_equal[["[in] Section", "in_out_is_equal"]]
                not_equal_link_res_and_combined_sec = pd.merge(search_on_combined_for_not_equal, locate_result_combined_sections_df, on='[in] Section', how='left')
                not_equal_link_res_and_combined_sec['Chip'] = not_equal_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Chip'].values[0] if x in locate_result_sections_df['Section'].values else np.NaN)
                not_equal_link_res_and_combined_sec['Group addr'] = not_equal_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Space addr'].values[0] if x in locate_result_sections_df['Section'].values else np.NaN)
                not_equal_link_res_and_combined_sec['Space addr'] = not_equal_link_res_and_combined_sec.apply(lambda row: '0x' + hex(int(row['Group addr'], 16) + int(row['[out] Offset'], 16))[2:].zfill(8) if not pd.isna(row['Group addr']) else np.NaN, axis=1)
                not_equal_merged = not_equal_link_res_and_combined_sec[["Chip", "Space addr", "[in] Size (MAU)", "in_out_is_equal", "[in] Section", "[out] Section"]]
                not_equal_merged = not_equal_link_res_and_combined_sec.rename(columns={"[in] Size (MAU)" : "Size (MAU)"})
            else:
                not_equal_merged = not_equal_link_res_sec
            print_message("warning", "Could be 2 or more symbol in the same space adrress:\n" + str(not_equal_merged["Space addr"].unique().tolist()))


        ############ Locate Result Sections Part  ############################
        merged_link_res_and_sec = pd.merge(link_result_df_for_sec, locate_result_sections_df_renamed, on='[out] Section', how='left')

        # check if could not found on Chip
        search_on_combined = merged_link_res_and_sec[merged_link_res_and_sec["Chip"].isna()]
        merged_link_res_and_sec = merged_link_res_and_sec.drop(search_on_combined.index)

        merged_link_res_and_sec = pd.merge(merged_link_res_and_sec, symbols_df, on='Space addr', how='left')
        merged_link_res_and_sec["Name"] = merged_link_res_and_sec["Name"].fillna("Not Found in Sections Table")


        ############ Locate Result Combined Sections Part  ############################
        if not search_on_combined.empty:
            search_on_combined = search_on_combined[["[in] Section","in_out_is_equal"]]

            merged_link_res_and_combined_sec = pd.merge(search_on_combined, locate_result_combined_sections_df, on='[in] Section', how='left')
            merged_link_res_and_combined_sec['Chip'] = merged_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Chip'].values[0] if x in locate_result_sections_df['Section'].values else np.NaN)
            merged_link_res_and_combined_sec['Group addr'] = merged_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Space addr'].values[0] if x in locate_result_sections_df['Section'].values else np.NaN)
            merged_link_res_and_combined_sec['Space addr'] = merged_link_res_and_combined_sec.apply(lambda row: '0x' + hex(int(row['Group addr'], 16) + int(row['[out] Offset'], 16))[2:].zfill(8) if not pd.isna(row['Group addr']) else np.NaN, axis=1)

            merged_link_res_and_combined_sec = pd.merge(merged_link_res_and_combined_sec, symbols_df, on='Space addr', how='left')
            merged_link_res_and_combined_sec["Name"] = merged_link_res_and_combined_sec["Name"].fillna("Not Found in Combined Sections Table")
            merged_link_res_and_combined_sec = merged_link_res_and_combined_sec.rename(columns={"[in] Size (MAU)" : "Size (MAU)"})

        if not not_equals_table.empty:
            # not_equal_merged['Name'] = 'Not Searched (In Out Section Different)'
            if not search_on_combined.empty:
                all_merged = pd.concat([merged_link_res_and_sec, merged_link_res_and_combined_sec, not_equal_merged], axis=0)
            else:
                all_merged = pd.concat([merged_link_res_and_sec, not_equal_merged], axis=0)
        else:
            if not search_on_combined.empty:
                all_merged = pd.concat([merged_link_res_and_sec, merged_link_res_and_combined_sec], axis=0)
            else:
                all_merged = merged_link_res_and_sec
        # all_merged = all_merged.dropna() 
        all_merged = all_merged.rename(columns={"Name" : "Symbol Name"})
        # reorder
        cols = ['Chip', 'Space addr', 'Size (MAU)', 'Symbol Name', 'in_out_is_equal', '[in] Section', '[out] Section']
        all_merged = all_merged[cols]
        all_merged = all_merged.reset_index(drop=True)
        MapFileTable().save_df_as(all_merged, name='file_info_'+ file_name, format='html')
        if all_merged["Chip"].isna().all(): raise ValueError("Kodda bir hata var")
        # show(all_merged)
        return all_merged
 
    def get_overall(self):
        self.map_parser.init_tables(["overall"])
        overall_df = self.map_parser.tables["overall"]
        
        self.show_table_gui_and_save(overall_df, "overall")
        return overall_df
    
    
    def get_specific_mem_usage(self):
        self.map_parser.init_tables(keys=["overall"])
        base_table = self.map_parser.tables["overall"]
        
        memory = base_table['Memory']
        
        # to remove total row, reassign the memory
        memory = memory[:-1]
        
        user_input_index = input(str(memory) + "\nEnter the memory type/types given above. Search key or index?: ")
        
        if not user_input_index.strip():
            print("Memory type cannot be empty.")
            self.get_specific_mem_usage()
            return
 
        try:
            user_input_index = int(user_input_index)
            if user_input_index < 1 or user_input_index > len(memory):
                raise ValueError("Please enter a number between 1 and " + str(len(memory)))
            print(base_table.iloc[user_input_index-1])
            return base_table.iloc[user_input_index-1]
        except ValueError:
            # if user input is not a number, search the memory type
            filtered_df = base_table[base_table["Memory"].str.contains(user_input_index, na=False, regex=False)]
            if filtered_df.empty:
                print("The memory type could not found in the table. Please enter a valid index or memory type.")
                return
            print(filtered_df)
            return filtered_df
 
 
    def get_symbol_info(self): # belirli bir sembolü bulur
        
        symbol_name = input("Enter the symbol name: ")
        if not symbol_name.strip():
            print("Symbol name cannot be empty.")
            self.get_symbol_info()
            return
        
        self.map_parser.init_tables(["locate_result_symbols_address"])
        symbols_table = self.map_parser.tables["locate_result_symbols_address"]  
        
        #adresses = symbols_table['Space addr']
        #symbols = symbols_table['Name']
        filtered_df = symbols_table.query('Name == "{}"'.format(symbol_name))
        if filtered_df.empty:
            print_message("warning", "The symbol could not found in Symbols table")     
            return
 
        self.map_parser.init_tables(["locate_result_sections", "cross_references"])
                            
        adress = filtered_df['Space addr']
 
        locate_res_sections_table = self.map_parser.tables["locate_result_sections"]
        filtered_locate_res_sections_df = locate_res_sections_table.query('`Space addr` == {}'.format(adress.values))
        if filtered_locate_res_sections_df.empty:
            print_message("warning","The symbol could not found in locate_res table")
        
        chip = filtered_locate_res_sections_df["Chip"].values[0]
        size = filtered_locate_res_sections_df["Size (MAU)"].values[0]
        section = filtered_locate_res_sections_df["Section"].values[0]
 
        section_type = self.map_parser.get_section_type(section)
        
        cross_references_table = self.map_parser.tables["cross_references"]
        cross_references_df = cross_references_table.query('Symbol == "{}"'.format(symbol_name))
        definition_file = cross_references_df["Definition file"].values[0]
        referenced_in = cross_references_df["Referenced in"].values[0]
        
        data = [[symbol_name, adress, chip, size, section_type, definition_file, referenced_in]]
        info_df = pd.DataFrame(data,columns=['Symbol', 'Adress', 'Chip', 'Size', 'SectionType', 'Definition File', 'Referenced In'])
        MapFileTable().save_df_as(info_df, name='symbol_info_'+symbol_name, format='html')
        for i in range(len(data[0])):
            print(info_df.columns[i] + ": " + str(data[0][i]))
            
        return info_df
 
    def get_table_from_map_file(self):
       
        # table names with \n and with numeric index
        str_tables = "\n".join([str(i+1) + ". " + table for i, table in enumerate(self.map_parser.tables.keys())])
       
        table_input = input("Enter the table name given below\n" + str_tables + "\n Table number: ")
       
        try:
            table_input = int(table_input)
            if table_input < 1 or table_input > len(self.map_parser.tables.keys()):
                raise ValueError("Please enter a number between 1 and " + str(len(self.map_parser.tables.keys())))
        except ValueError:
            print("Please enter a number between 1 and " + str(len(self.map_parser.tables.keys())))
            return
       
        selected_table = list(self.map_parser.tables.keys())[table_input-1]
        print("Selected table: ", selected_table)
       
        self.map_parser.init_tables(keys=[selected_table])
        table_df = self.map_parser.tables[selected_table]
        self.show_table_gui_and_save(table_df, selected_table)
    
    def show_table_gui_and_save(self, table_df, table_name):
        gui_input = input("Do you want to see the table in GUI? After you close the GUI, you will be asked to save the table with changes. (yes/no): ")
        if gui_input.lower() == "yes":
            gui = show(table_df)
       
            # check the is there any changes in the table with pandas
            gui_df = gui.get_dataframes()
           
            is_equal = pd.DataFrame.equals(table_df, gui_df["table_df"])
            save_input = input("Do you want to save the table with changes? (yes/no): ") if not is_equal else input("There is no change in the table. Do you want to save the table? (yes/no): ")
           
            if save_input == "yes":
                format_input = input("Enter the type of file you want to save (csv, xlsx, json, html): ")
                if format_input in ["csv", "xlsx", "json", "html"]:
                    MapFileTable().save_df_as(gui_df["table_df"], name='changed_' + table_name, format=format_input)
                    return gui_df["table_df"]
                else:
                    print("Invalid type")
                    return gui_df["table_df"]
            elif save_input.lower() == "no":
                print("Table is not saved.")
                return table_df
            else:
                print("Invalid input")
                return table_df
               
        elif gui_input.lower() == "no":    
            save_input2 = input("Do you want to save the table? (yes/no): ")
            if save_input2.lower() == "yes":
                format_input = input("Enter the type of file you want to save (csv, xlsx, json, html): ")
                if format_input in ["csv", "xlsx", "json", "html"]:
                    MapFileTable().save_df_as(table_df, name=table_name, format=format_input)
                    return table_df
                else:
                    print("Invalid type")
                    return table_df
            elif save_input2.lower() == "no":
                print("Table is not saved.")
                return table_df
            else:
                print("Invalid input")
                return table_df
        else:
            print("Invalid input")
            return table_df
 
if __name__ == "__main__":
    obj = Modes()
    # obj.get_overall()
    # obj.get_file_info("Rte.c")
    
    # obj.get_overall()

    # obj.get_mem_section_check()
    obj.get_layers_mem_usage()