from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from memolyzer.table import MapFileTable
# from memolyzer.cli import Cli
from pandasgui import show
import pandas as pd
 
temp_modes = {"symbol_info":None,
              "file_info": None,
              "overall": None,
              "specific_mem_usage": None,
              "mem_section_with_check": None,
              "get_table_from_map_file": None
              }
 
class Modes():
    def __init__(self) -> None:
        # self.args = Cli().get_args()
        self.map_parser = MapParser(MAP_FILE_PATH)
        self.modes = temp_modes
        
    def run_modes(self):
 
        mode_functions = {"symbol_info":self.map_parser.get_symbol_info, # tamamlandı
                          "overall": self.map_parser.init_overall, # percentage yazdırılacak
                          "specific_mem_usage": self.get_specific_mem_usage, # tek bir satırı döndürecek mesela dsrame göre
 
                          # test_mode_5 kullan
                          # excelin her satırı için passed yada failed
                          # eğer ki satır failse (expected içerisinde olmayan sembol, memory e.g. dsram1, ama bu expected da yok şeklinde string döndürecek)
                          "mem_section_with_check": None,  # excel den birden fazla alacak
 
                          # test_mode_5 kullan
                          "file_info": self.map_parser.get_file_info, # section, Referenced in çıkar, symbol gelicek size tablosu
                          # sorted on symbols de ara symbolu bul, size ve address yazdır
 
                          "get_table_from_map_file": self.get_table_from_map_file
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
 
 
    def get_overall(self):
        self.map_parser.init_overall()
        table = self.map_parser.tables["overall"]
        
        self.show_table_gui_and_save(table, "overall")
        return table
    
    
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
            print("The symbol could not found in Symbols table")     
            return
 
        self.map_parser.init_tables(["locate_result_sections", "cross_references"])
                            
        adress = filtered_df['Space addr']
 
        locate_res_sections_table = self.map_parser.tables["locate_result_sections"]
        filtered_locate_res_sections_df = locate_res_sections_table.query('`Space addr` == {}'.format(adress.values))
        if filtered_locate_res_sections_df.empty:
            print("The symbol could not found in locate_res table")
        
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
            elif save_input.lower == "no":
                print("Table is not saved.")
                return table_df
            else:
                print("Invalid input")
                return table_df
               
        elif gui_input.lower() == "no":    
            save_input2 = input("Do you want to save the table? (yes/no): ")
            if save_input2.lower == "yes":
                format_input = input("Enter the type of file you want to save (csv, xlsx, json, html): ")
                if format_input in ["csv", "xlsx", "json", "html"]:
                    MapFileTable().save_df_as(table_df, name=table_name, format=format_input)
                    return table_df
                else:
                    print("Invalid type")
                    return table_df
            elif save_input2.lower == "no":
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
    obj.get_specific_mem_usage()