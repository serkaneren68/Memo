
import regex as re
from prettytable import PrettyTable 
import pandas as pd
import os
import errno
from enum import Enum
from typing import List
 
class MapFileEntryTypes(Enum):
    HEX = 1
    SECTION = 2
    FILE = 3
    LIB = 4
    UNKNOWN = 5

hex_pattern = re.compile(r"0x[0-9a-fA-F]*")
section_pattern = re.compile(r"(.+)*\(([0-9]+)\)")
file_pattern = re.compile(r".+\.obj$")
lib_pattern = re.compile(r".+\.o$")

class MapFileTable():
    table_border_pattern = re.compile(r"[\+]+\-+\+$")

    def __init__(self) -> None:
        pass
    
    # TODO: map dosyasındaki tablolar incelendiğinde farklı türde verilerin varlığı tespit edildi örneğin dosya ile ilgili olan girdiler 
    # .obj ile bitiyor yada section ile ilgili olan girdiler (sayı) ile bitiyor
    # regex ifadesi ile herbir girdi türünün formatını yakalamaya zorlanabilir.
    def get_table_from_txt(self, lines, header_pattern_statement):
        table_founded = False
        rows = list()
        header_pattern = re.compile(header_pattern_statement)
        header_found = False
        for j in range(len(lines)):
            header_obj = re.search(header_pattern, lines[j])
            if(header_obj):
                header_found = True
                continue

            if header_found:
                if not table_founded:
                    table_border_obj = re.search(self.table_border_pattern, lines[j])
                    if(table_border_obj):
                        table_founded = True
                        continue
                if table_founded: # with +---+ pattern
                    table_border_obj = re.search(self.table_border_pattern, lines[j])

                    if(table_border_obj): # end of table
                        table_founded = False
                        break

                    if lines[j].startswith("|") :
                        row =[ i.rstrip().lstrip() for i in lines[j].split("|")[1:-1] ]  # ilk ve son boş sütunları atla
                        if len(row)<=1: continue # tablo olması için en az 2 eleman olmalı
                        if row[0] == "": # satırın ilk elemanı boş ise 
                            for column_num in range(len(rows[-1])):
                                if row[column_num] != "":  # boş değilse
                                    # eğer son eleman virgül ile bitiyorsa boşluk bırakarak ekle değilse normal ekle
                                    # örnek olarak 73818. satır *_D.map
                                    if row[column_num][-1] == ",":
                                        rows[-1][column_num] = rows[-1][column_num] + " " + row[column_num]  
                                    else: rows[-1][column_num] = rows[-1][column_num] + row[column_num]
                        else:
                            rows.append(row)
                        rows[-1] = self.type_fit(rows[-1])
        return rows

    # TODO: iki farklı type ı aynı rowda buldum bu çözülmeli .rodata.Dcm_Lcfg_Dsd.Dcm_Cfg_SrvTab0_Service0x11_SubSrv_acst 91428 hex ve section
    def type_finder(self, cell_value):
        if re.search(section_pattern, cell_value):
            return MapFileEntryTypes.SECTION, re.findall(section_pattern, cell_value)
        elif re.search(hex_pattern, cell_value):
            return MapFileEntryTypes.HEX, re.findall(hex_pattern, cell_value)
        elif re.search(file_pattern, cell_value):
            return MapFileEntryTypes.FILE, re.findall(file_pattern, cell_value)
        elif re.search(lib_pattern, cell_value):
            return MapFileEntryTypes.LIB, re.findall(lib_pattern, cell_value)
        else:
            return MapFileEntryTypes.UNKNOWN, None

    def type_fit(self, merged_row:list):
        for col in range (len(merged_row)):
            map_type, findings = self.type_finder(merged_row[col])
            if map_type == MapFileEntryTypes.SECTION:
                # eğer section number lara ulaşılmak istenirse findings[0][1] ile ulaşılabilir.
                merged_row[col] = findings[0][0].strip() + " " + findings[0][1]
        return merged_row

    def convert_to_data_frame(self, rows):
        df = pd.DataFrame(rows)
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header
        return df
    
    def save_df_as_html(self,df,name='temp.html'):
        text_file = open(name, "w")
        text_file.write(df.to_html())
        text_file.close()
    
    #TODO: Add titles feature for each df
    def save_multiple_df_as_html(self,df_list,name):
        text_file = open(name, "w")
        html_content = ""
        for df in df_list:
            html_content = html_content + df.to_html() + "\n\n"
        text_file.write(html_content)
        text_file.close()        

    def get_table_from_txt_tool_invocation(self, lines, header_pattern_statement, row0_pattern: str = "CMakeFiles", row1_pattern_list: List[str] = ['CMakeFiles', '"C:/ProgramData']) -> List[str]:     
        table_founded = False
        rows = list()
        header_pattern = re.compile(header_pattern_statement)
        header_found = False
        cmake_pattern_row0_founded = False
        for j in range(len(lines)):
            header_obj = re.search(header_pattern, lines[j])
            if(header_obj):
                header_found = True
                continue
            if header_found:
                if not table_founded:
                    table_border_obj = re.search(self.table_border_pattern, lines[j])
                    if(table_border_obj):
                        table_founded = True
                        continue
                if table_founded: # with +---+ pattern
                    table_border_obj = re.search(self.table_border_pattern, lines[j])

                    if(table_border_obj): # end of table
                        table_founded = False
                        break

                    if lines[j].startswith("|") :
                        row =[ i.rstrip().lstrip() for i in lines[j].split("|")[1:-1] ]  # ilk ve son boş sütunları atla
                        if len(row)<=1: continue # tablo olması için en az 2 eleman olmalı
                        if row[0] == "" and not cmake_pattern_row0_founded: 
                            for column_num in range(len(rows[-1])):
                                if row[column_num] != "":  # ["def","abc"] gibi boş değilse
                                    rows[-1][column_num] = rows[-1][column_num] + " " + row[column_num]  
                                    
                        elif row0_pattern in row[0]:
                            cmake_pattern_row0_founded = True
                            rows.append(row)
                            continue
                        
                        elif row[0] != "" and not cmake_pattern_row0_founded: # satırın ilk elemanı dolu ve aranan row0_pattern bulunmadıysa
                            rows.append(row)
                            
                        elif row[0] != "" and cmake_pattern_row0_founded:
                            cmake_pattern_row0_founded = False
                            rows.append(row)
                        
                        if row[0] == "" and cmake_pattern_row0_founded: # satırın ilk elemanı boş ve row0_pattern bulunduysa
                            for row1_pattern in row1_pattern_list: # patternin en başına ", " ekle
                                if row1_pattern in row[1]:
                                    row[1] = row[1].replace(row1_pattern.strip(), f", {row1_pattern}")
                            rows[-1][1] = rows[-1][1] + row[1]
        return rows

    def get_table_from_txt_combined_sections(self, lines, header_pattern_statement=r"\* Combined sections") -> List[str]:     
        table_founded = False
        rows = list()
        header_pattern = re.compile(header_pattern_statement)
        header_found = False
        for j in range(len(lines)):
            header_obj = re.search(header_pattern, lines[j])
            if(header_obj):
                header_found = True
                continue
            if header_found:
                if not table_founded:
                    table_border_obj = re.search(self.table_border_pattern, lines[j])
                    if(table_border_obj):
                        table_founded = True
                        continue
                if table_founded: # with +---+ pattern
                    table_border_obj = re.search(self.table_border_pattern, lines[j])

                    if(table_border_obj): # end of table
                        table_founded = False
                        break

                    if lines[j].startswith("|") :
                        row =[ i.rstrip().lstrip() for i in lines[j].split("|")[1:-1] ]  # ilk ve son boş sütunları atla
                        if len(row)<=1: continue # tablo olması için en az 2 eleman olmalı
                        # alt satıra geçerken referansı hex olarak aldım 
                        if row[1] == "" and len(rows) > 0:
                            for column_num in range(len(rows[-1])):
                                if row[column_num] != "":
                                    rows[-1][column_num] = rows[-1][column_num] + row[column_num]
                        else:
                            if row[3] == "" and len(rows) > 0:
                                row[3] = rows[-1][3]
                            rows.append(row)
                        rows[-1] = self.type_fit(rows[-1])
        return rows

    def save_df_as(self, df, name, format):
        if format not in ["html","csv","xlsx","json"]:
            print("The format is not supported!")
            return
        
        # folder directory saved/{format}/{name}.{format}
        directory = os.path.join("saved", format, name + "." + format)

        # try to create folder
        try:
            os.makedirs(os.path.dirname(directory), exist_ok=True)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

        if format == "html":
            df.to_html(directory)
        elif format == "csv":
            df.to_csv(directory, index=False, header=True)
        elif format == "xlsx":
            df.to_excel(directory, index=False, header=True)
        elif format == "json":
            df.to_json(directory)
        
        print("Saved as ",format," at ",os.path.abspath(directory))
    
