import unittest
from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from memolyzer.table import MapFileTable
from pandasgui import show
import pandas as pd
 
class TestMapParser(unittest.TestCase):
    map_parser = MapParser(MAP_FILE_PATH)
 
    # def test_get_file_parts(self):
    #     self.assertEqual(len(self.map_parser.headers), 9)
    #     self.assertEqual(self.map_parser.headers[0]["title"], "Tool and Invocation")
    #     self.assertEqual(self.map_parser.headers[1]["title"], "Used Resources")
    #     self.assertEqual(self.map_parser.headers[2]["title"], "Processed Files")
    #     self.assertEqual(self.map_parser.headers[3]["title"], "Link Result")
    #     self.assertEqual(self.map_parser.headers[4]["title"], "Cross References")
    #     self.assertEqual(self.map_parser.headers[5]["title"], "Call Graph")
    #     self.assertEqual(self.map_parser.headers[6]["title"], "Overlay")
    #     self.assertEqual(self.map_parser.headers[7]["title"], "Locate Result")
    #     self.assertEqual(self.map_parser.headers[8]["title"], "Locate Rules")
 
    def test_get_tool_and_invocation(self):
        self.map_parser.init_tables(["tool_and_invocation"])
        result = self.map_parser.tables["tool_and_invocation"]
        # arr = result["Invocation"][3].split(",") # split by comma
        # arr = [i.strip() for i in arr]
        # print(arr)
        MapFileTable().save_df_as(result,"tool_and_invocation","html")
        # show(result)
 
    def test_get_overall(self):
        self.map_parser.init_tables(["overall"])
        result = self.map_parser.tables["overall"]
        MapFileTable().save_df_as(result,"overall","html")
        # show(result)
        
    def test_get_link_result(self):
        self.map_parser.init_tables(["link_result"])
        result = self.map_parser.tables["link_result"]
        MapFileTable().save_df_as(result,"link_result","html")
        # show(result)
        
    def test_get_cross_referenfes(self):
        self.map_parser.init_tables(["cross_references"])
        result = self.map_parser.tables["cross_references"]
        MapFileTable().save_df_as(result,"cross_references","xlsx")
        # show(result)
        
    def test_get_locate_results_sections(self):
        self.map_parser.init_tables(["locate_result_sections"])
        result = self.map_parser.tables["locate_result_sections"]
        MapFileTable().save_df_as(result,"locate_result_sections","html")
        # show(result)
        
    def test_get_symbols_by_name(self):
        self.map_parser.init_tables(["locate_result_symbols_name"])
        result = self.map_parser.tables["locate_result_symbols_name"]
        MapFileTable().save_df_as(result,"symbols_by_name","html")
        # show(result)
        
    def test_get_symbols_by_adress(self):
        self.map_parser.init_tables(["locate_result_symbols_address"])
        result = self.map_parser.tables["locate_result_symbols_address"]
        MapFileTable().save_df_as(result,"symbols_by_adress","json")
        # show(result)
 
    def test_get_combined_sections(self):
        self.map_parser.init_tables(["locate_result_combined_sections"])
        result = self.map_parser.tables["locate_result_combined_sections"]
        MapFileTable().save_df_as(result,"combined_sections","html")
        # show(result)
        
    def test_get_symbol_info(self):
        result = self.map_parser.get_symbol_info("adc_rawData_I_A_TSIER") #adc_analogRead_Init
        # show(result)
    
    def test_get_link_result_by_file_name(self):
        result = self.map_parser.get_link_result_by_file_name("SWintegration_FD.c")
        print(result)
        
    def test_get_file_info(self):
        result1, result2, result3 = self.map_parser.get_file_info("SWintegration_FD.c") #v2g_vehToGrid.c
        show(result1,result2,result3)

    def test_mode(self):
        link_result_df = self.map_parser.get_link_result_by_file_name("Adc.c")
        matched_sections_df, matched_link_result_df, not_matched_link_result_df = self.map_parser.match_link_result_and_sections(link_result_df)
        matched_combined_sections_df, matched_last_link_result_df, not_matched_last_link_result_df = self.map_parser.match_link_result_and_combined_sections(not_matched_link_result_df)


        matched_sections_df = matched_sections_df.rename(columns={"Section": "[in] Section"})
        matched_sections_df = matched_sections_df.drop(columns=['Chip addr', 'Alignment', 'Size (MAU)'])
        # matched_link_result_df = matched_link_result_df.rename(columns={"[in] Section": "Section"})
        merged_link_result_and_sections = pd.merge(matched_link_result_df, matched_sections_df, on='[in] Section')
        show(merged_link_result_and_sections)

        # # Alttaki sıralarına göre eşlemiyor
        # new_df = matched_link_result_df
        # new_df["Chip"]       = matched_sections_df["Chip"].values
        # new_df["Space addr"] = matched_sections_df["Space addr"].values
        # new_df["Size (MAU)"] = matched_sections_df["Size (MAU)"].values
        # show(result, new_df)

        print("\n------------------")
        print("get_link_result_by_file_name shape:", link_result_df.shape)
        print("\n------------------")
        print(matched_sections_df.shape)
        print(matched_link_result_df.shape)
        print(not_matched_link_result_df.shape)
        print("\n------------------")
        print(matched_combined_sections_df.shape)
        print(matched_last_link_result_df.shape)
        print(not_matched_last_link_result_df.shape)

        print("\n------------------")
        print(merged_link_result_and_sections.shape[0])

        # TODO: bu yanlış düzelt

        # last_out_section = ""
        # for i, row in matched_combined_sections_df.iterrows():
        #     if last_out_section != row['[out] Section']:
        #         deneme = self.map_parser.tables["locate_result_sections"][self.map_parser.tables["locate_result_sections"]['Section'].isin(matched_combined_sections_df['[out] Section'])]
        #         print(deneme)

        # i = 0
        # for row in matched_combined_sections_df.iterrows():
        #     print(f"İter: {i}")
        #     print(row)
        #     i = i + 1
        
        # i = 0
        # for row in deneme.iterrows():
        #     print(f"İter: {i}")
        #     print(row)
        #     i = i + 1

    def test_mode_5(self):

        link_result_df = self.map_parser.get_link_result_by_file_name("Adc.c")
        self.map_parser.init_tables(["locate_result_sections"])
        locate_result_sections_df = self.map_parser.tables["locate_result_sections"]
        locate_result_sections_df = locate_result_sections_df.rename(columns={"Section": "[in] Section"})
        merged_link_res_and_sec = pd.merge(link_result_df, locate_result_sections_df, on='[in] Section', how='inner')

        self.map_parser.init_tables(["locate_result_combined_sections"])
        locate_result_combined_sections_df = self.map_parser.tables["locate_result_combined_sections"]
        locate_result_combined_sections_df = locate_result_combined_sections_df.drop(columns=['[in] Size (MAU)', '[out] Offset', 'Size (MAU)'])
        merged_link_res_and_combined_sec = pd.merge(link_result_df, locate_result_combined_sections_df, on='[in] Section', how='inner', suffixes=('_link_res', '_locate_res'))

        show(merged_link_res_and_sec, merged_link_res_and_combined_sec)

if __name__ == '__main__':
    unittest.main()