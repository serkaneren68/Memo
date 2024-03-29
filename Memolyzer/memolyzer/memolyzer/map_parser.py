
import regex as re
import os
from pathlib import Path
# from prettytable import PrettyTable 
from memolyzer.table import MapFileTable 
import pandas as pd

def read_file_line_by_line(file):
    try:
        f = open(file, "r")
        lines = f.readlines()
        f.close()
        return lines
    except Exception:
        print("Could not read to file")


PROCESSED_FILES = "/^[\*]+\s*Processed Files\s*[\*]+$/"
LINK_RESULTS = "/^[\*]+\s*Link Result\s*[\*]+$/"
LOCATE_RESULTS = "/^[\*]+\s*Locate Result\s*[\*]+$/"
USED_RESOURCES = "/^[\*]+\s*Used Resources\s*[\*]+$/"
UNKNOWN = "/^[\*]* .* [\*]*$/"

MAP_FILE_NAME = "CEER_VCU_APP_V1_D_1.elf.map"
MAP_FILE_PATH = os.path.normpath(os.path.join(Path(__file__).parent.absolute(),os.pardir,"example-data",MAP_FILE_NAME))
 
temp_tables = {
    "tool_and_invocation": None,
    "overall": None,
    "link_result": None,
    "cross_references": None,
    "locate_result_sections": None,
    "locate_result_symbols_name": None,
    "locate_result_symbols_address": None,
    "combined_sections": None,
}
 
class MapParser:
    def __init__(self, map_file_path) -> None:
        self.map_file_path = map_file_path
        self.map_file = read_file_line_by_line(self.map_file_path)
        self.headers = list(dict())
        self.headers = self.get_file_parts()
        self.tables = temp_tables
    
    def update_tables(self, keys:list):
 
        task_functions = {
            "tool_and_invocation": self.update_tool_and_invocation,
            "overall": self.update_overall,
            "link_result": self.update_link_result,
            "cross_references": self.update_cross_references,
            "locate_result_sections": self.update_locate_results_sections,
            "locate_result_symbols_name": self.update_symbols_by_name,
            "locate_result_symbols_address": self.update_symbols_by_adress,
            "locate_result_combined_sections": self.update_combined_sections,
        }
        
        if keys == ["all"]:
            for key in list(task_functions.keys()):
                self.tables[key] = task_functions[key]()
            return
            
        for key in keys:
            if key in list(task_functions.keys()):
                self.tables[key] = task_functions[key]()
            else:
                print(f"Invalid key '{key}'.")
 
    def get_tables(self, key_list) -> dict:
        
        if key_list == ["all"]:
            return self.tables
        
        tables = dict()
        for key in key_list:
            if key in self.tables:
                tables[key] = self.tables[key]
            else:
                print(f"Invalid key '{key}'.")
        return tables
    
    def get_file_parts(self):
        
        header_pattern = re.compile(r"^[\*]+\s*(?P<header>[a-zA-Z0-9 ]+)\s*[\*]+$")
 
        for line in self.map_file:
            header_match_object =  re.search(header_pattern, line)
            if(header_match_object):
                header = {"title":header_match_object.group('header').rstrip(),
                          "start_line": self.map_file.index(line),
                          "end_line"  : len(self.map_file)
                          }
                self.headers.append(header)
                if self.headers:
                    self.headers[self.headers.index(header)-1]["end_line"] = self.map_file.index(line) - 1
                    
        return self.headers
    
    def get_header_info(self, header):
        for head in self.headers:
            if(head["title"] == header):
                return head
        return None
 
    def update_tool_and_invocation(self):
        start_line = self.get_header_info("Tool and Invocation")["start_line"]
        end_line = self.get_header_info("Tool and Invocation")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt_tool_invocation(lines,r"[\*]+\s*Tool and Invocation\s*[\*]+")
        table = pd.DataFrame(rows, columns=["Tool","Invocation"])
        return table
    
    def update_overall(self):
        start_line = self.get_header_info("Used Resources")["start_line"]        
        end_line = self.get_header_info("Used Resources")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt(lines,r"\* Memory usage in bytes")
        base_table = MapFileTable().convert_to_data_frame(rows)
        
        #memory usage percentages
        percentage =  [(int(total,16)-int(free,16)) / int(total,16) * 100
                       for free,total in zip(base_table['Free'],base_table['Total'])]         
        base_table['overall'] = percentage
        return base_table
 
    def update_link_result(self):
        start_line = self.get_header_info("Link Result")["start_line"]        
        end_line = self.get_header_info("Link Result")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt(lines, r"[\*]+\s*Link Result\s*[\*]+" )
        
        # rows, sections = MapFileTable().get_table_from_txt(lines, r"[\*]+\s*Link Result\s*[\*]+", is_link_result=True)
        
        # print("Number of section_number: ", sections.count("section_number"))
        # if sections.count("section_number") > 1: raise Exception("There are more than one section_number")
        # if len(sections) != len(rows): raise Exception("Number of sections and rows are not equal. Can not merge.")
        
        # # merge rows and sections as a new column
        # for i in range(len(rows)): rows[i].append(sections[i])
        
        # convert to pandas data frame
        
        table = MapFileTable().convert_to_data_frame(rows)
        return table
 
    def update_cross_references(self):
        start_line = self.get_header_info("Cross References")["start_line"]        
        end_line = self.get_header_info("Cross References")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt(lines,r"[\*]+\s*Cross References\s*[\*]+")
        table = MapFileTable().convert_to_data_frame(rows)
        return table
 
    def update_locate_results_sections(self):
        start_line = self.get_header_info("Locate Result")["start_line"]        
        end_line = self.get_header_info("Locate Result")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt(lines,r"\* Sections")
        table = MapFileTable().convert_to_data_frame(rows)
        return table
 
    def update_symbols_by_name(self):
        start_line = self.get_header_info("Locate Result")["start_line"]        
        end_line = self.get_header_info("Locate Result")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt(lines,r"\* Symbols \(sorted on name\)")
        table = MapFileTable().convert_to_data_frame(rows)
        return table
        
    def update_symbols_by_adress(self):
        start_line = self.get_header_info("Locate Result")["start_line"]        
        end_line = self.get_header_info("Locate Result")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt(lines,r"\* Symbols \(sorted on address\)")
        table = MapFileTable().convert_to_data_frame(rows)
        return table
 
    def update_combined_sections(self):
        start_line = self.get_header_info("Locate Result")["start_line"]
        end_line = self.get_header_info("Locate Result")["end_line"]
        lines = self.map_file[start_line:end_line]
        rows = MapFileTable().get_table_from_txt_combined_sections(lines)
        table = MapFileTable().convert_to_data_frame(rows)
        return table

    def get_symbol_info(self, symbol_name): # belirli bir sembolü bulur 
        
        self.update_tables(["locate_result_symbols_address",
                            "locate_result_sections",
                            "cross_references"])
        
        symbols_table = self.tables["locate_result_symbols_address"]  
        
        #adresses = symbols_table['Space addr']
        #symbols = symbols_table['Name']
        filtered_df = symbols_table.query('Name == "{}"'.format(symbol_name))
        if filtered_df.empty:
            print("The symbol could not found in Symbols table")     

        adress = filtered_df['Space addr']

        # cross_ref_table = self.get_cross_referenfes()
        # filtered_ref_df = cross_ref_table.query('Symbol == "{}"'.format(symbol_name))
        # if filtered_ref_df.empty:
        #     print("The symbol could not found in cross references table")     

        # definition_section = filtered_ref_df["Definition section"]
        # section_id_obj = re.compile(r"\({1}(?P<section_id>[a-zA-Z0-9 ]+)\){1}")
        # section_id = re.search(section_id_obj,definition_section)

        locate_res_sections_table = self.tables["locate_result_sections"]
        space_adresses = locate_res_sections_table.columns[4]
        filtered_locate_res_sections_df = locate_res_sections_table.query('`Space addr` == {}'.format(adress.values))
        if filtered_locate_res_sections_df.empty:
            print("The symbol could not found in locate_res table") 
        chip = filtered_locate_res_sections_df["Chip"]
        size = filtered_locate_res_sections_df["Size (MAU)"]
        section = filtered_locate_res_sections_df["Section"]

        section_type = self.get_section_type(section.values[0])
        
        cross_references_table = self.tables["cross_references"]
        cross_references_df = cross_references_table.query('Symbol == "{}"'.format(symbol_name))
        definition_file = cross_references_df["Definition file"].values
        referenced_in = cross_references_df["Referenced in"].values
        
        data = [[symbol_name, adress.values, chip.values, size.values, section_type, definition_file, referenced_in]]
        info_df = pd.DataFrame(data,columns=['Symbol', 'Adress', 'Chip', 'Size', 'SectionType', 'Definition File', 'Referenced In'])
        MapFileTable().save_df_as_html(info_df,"test-symbol_info.html")

        return info_df

        # symbol_column = link_results_sub_df.apply(
        #                     lambda x: self.get_symbol_name_from_section(x["[in] Section"]),axis=1)
        # link_results_sub_df["Symbol"] = symbol_column
        
    def get_file_info(self, file_name):
        #TODO: add file check implementation using Used Resources
        self.update_tables(["cross_references"])
        self.update_tables(["link_result"])
        file_name_with_suffix = file_name + ".obj"
        cross_references_table = self.tables["cross_references"]
        referenced_in_df = cross_references_table.query("`Referenced in`.str.match('{}')".format(file_name_with_suffix))

        cross_references_df = cross_references_table.query('`Definition file` == "{}"'.format(file_name_with_suffix))
        if cross_references_df.empty:
            print("The file could not found in Cross_References table") 
        
        link_result_table = self.tables["link_result"]
        link_result_table_df = link_result_table.query('`[in] File` == "{}"'.format(file_name_with_suffix))   
        self.match_link_result_and_sections(link_result_table_df)    
        if link_result_table_df.empty:
            print("The file could not found in Link_Result table")    
        MapFileTable().save_multiple_df_as_html([cross_references_df, link_result_table_df, referenced_in_df],"test-file_info.html")
        return cross_references_df, link_result_table_df, referenced_in_df


    def match_link_result_and_combined_sections(self, link_results_df):
        self.update_tables(["locate_result_combined_sections"])
        locate_result_combined_sections = self.tables["locate_result_combined_sections"]
        matced_df = locate_result_combined_sections[locate_result_combined_sections['[in] Section'].isin(link_results_df['[in] Section'])]
        # print(matced_df)
        return matced_df
        
    def match_link_result_and_sections(self, link_results_df):
        self.update_tables(["locate_result_sections"])
        locate_result_sections = self.tables["locate_result_sections"]
        df3 = locate_result_sections[locate_result_sections['Section'].isin(link_results_df['[in] Section'])]
       
        # if link_results_df.shape[0] != df3.shape[0]:
        #     matced_df = self.match_link_result_and_combined_sections(link_results_df)
        #     print(matced_df)
        #     # raise Exception("Sorry, row counts are not same")
        # else:
        #     link_results_df["Chip"] = df3["Chip"].values
        #     link_results_df["Space addr"] = df3["Space addr"].values
        #     link_results_df["Size (MAU)"] = df3["Size (MAU)"].values
       
        return df3
    
    # path to 
    # This function is used to get the link result of a file
    def get_link_result_by_file_name(self, file_name):
        self.update_tables(["link_result"])
        file_name_with_suffix = file_name + ".obj"
        link_result_table = self.tables["link_result"]
        link_result_table_df_by_file = link_result_table.query('`[in] File` == "{}"'.format(file_name_with_suffix))

        matched_link_results = self.match_link_result_and_sections(link_result_table_df_by_file)
        MapFileTable().save_df_as(matched_link_results,"matched_link_results","html")
        print(matched_link_results)
        return link_result_table_df_by_file

    def get_section_type(self, section):
        if section.startswith(".bss"):
            return "bss"
        elif section.startswith(".data"):
            return "data"
        elif section.startswith(".text"):
            return "text"
        else:
            return "others"

    def get_overview_of_map_file(self):
        """_summary_: This function should return a dictionary that show all
        of the Tables in the Map file structure. For ex.
        {
            Used Resources:{
                Table1,
                Table2,
                ...
            }
            Locate Result{
                Table1,
                Table2,
                ...
            }
        }
        """