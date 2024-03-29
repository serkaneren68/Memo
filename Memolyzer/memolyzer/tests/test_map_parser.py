import unittest
from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from memolyzer.table import MapFileTable
# from pandasgui import show
 
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
        self.map_parser.update_tables(["tool_and_invocation"])
        result = self.map_parser.tables["tool_and_invocation"]
        # arr = result["Invocation"][3].split(",") # split by comma
        # arr = [i.strip() for i in arr]
        # print(arr)
        MapFileTable().save_df_as(result,"tool_and_invocation","html")
        # show(result)
 
    def test_get_overall(self):
        self.map_parser.update_tables(["overall"])
        result = self.map_parser.tables["overall"]
        MapFileTable().save_df_as(result,"overall","html")
        # show(result)
        
    def test_get_link_result(self):
        self.map_parser.update_tables(["link_result"])
        result = self.map_parser.tables["link_result"]
        MapFileTable().save_df_as(result,"link_result","html")
        # show(result)
        
    def test_get_cross_referenfes(self):
        self.map_parser.update_tables(["cross_references"])
        result = self.map_parser.tables["cross_references"]
        MapFileTable().save_df_as(result,"cross_references","xlsx")
        # show(result)
        
    def test_get_locate_results_sections(self):
        self.map_parser.update_tables(["locate_result_sections"])
        result = self.map_parser.tables["locate_result_sections"]
        MapFileTable().save_df_as(result,"locate_result_sections","html")
        # show(result)
        
    def test_get_symbols_by_name(self):
        self.map_parser.update_tables(["locate_result_symbols_name"])
        result = self.map_parser.tables["locate_result_symbols_name"]
        MapFileTable().save_df_as(result,"symbols_by_name","html")
        # show(result)
        
    def test_get_symbols_by_adress(self):
        self.map_parser.update_tables(["locate_result_symbols_address"])
        result = self.map_parser.tables["locate_result_symbols_address"]
        MapFileTable().save_df_as(result,"symbols_by_adress","json")
        # show(result)
 
    def test_get_combined_sections(self):
        self.map_parser.update_tables(["locate_result_combined_sections"])
        result = self.map_parser.tables["locate_result_combined_sections"]
        for i in result["[out] Section"]:
            print(i) if i not in [None, ""] else None
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
        # show(result1, result2, result3)

    def test_match_link_result_and_combined_sections(self):
        link_result = self.map_parser.get_link_result_by_file_name("Adc.c")
        result = self.map_parser.match_link_result_and_combined_sections(link_result)
        result2 = self.map_parser.match_link_result_and_sections(link_result)

        # for i in range(link_result.shape[0]):
        #     print(link_result.iloc[i, :])
            
        i = 0
        for row in link_result.iterrows():
            print(f"İter: {i}")
            print(row)
            i = i + 1

        print("\n\nresult------------------")
        i = 0
        for row in result.iterrows():
            print(f"İter: {i}")
            print(row)
            i = i + 1

        print("\n\nResult 2--------------------")
        i = 0
        for row in result2.iterrows():
            print(f"İter: {i}")
            print(row)
            i = i + 1

        # print(result)
        # # print(result2)
        print(result.shape)
        print(result2.shape)

        print("link_result shape:", link_result.shape)

if __name__ == '__main__':
    unittest.main()