import unittest
from memolyzer.map_parser import MapParser, MAP_FILE_PATH
from memolyzer.table import MapFileTable
from pandasgui import show
import pandas as pd
import logging as log
log.basicConfig(level=log.WARN, format='%(asctime)s - Project Memory Analyzer: %(message)s')

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
        df = self.map_parser.get_file_type()
        print(df)
 
    def test_get_overall(self):
        self.map_parser.init_tables(["overall"])
        result = self.map_parser.tables["overall"]
        MapFileTable().save_df_as(result,"overall","html")
        log.warn("unable to find")
        # show(result)

    def test_processed_files(self):
        self.map_parser.init_tables(["processed_files"])
        result = self.map_parser.tables["processed_files"]
        MapFileTable().save_df_as(result,"processed_files","html")
        show(result)

    def test_get_link_result(self):
        self.map_parser.init_tables(["link_result"])
        result = self.map_parser.tables["link_result"]
        MapFileTable().save_df_as(result,"link_result","xlsx")
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
        MapFileTable().save_df_as(result,"symbols_by_adress","html")
        # show(result)

    def test_get_combined_sections(self):
        self.map_parser.init_tables(["locate_result_combined_sections"])
        result = self.map_parser.tables["locate_result_combined_sections"]
        MapFileTable().save_df_as(result,"combined_sections","html")
        # show(result)

    def test_get_symbol_info(self):
        result = self.map_parser.get_symbol_info("adc_rawData_I_A_TSIER") #adc_analogRead_Init
        show(result)

    def test_get_link_result_by_file_name(self):
        result = self.map_parser.get_link_result_by_file_name("SWintegration_FD.c")
        print(result)

    def test_get_file_info(self):
        result1, result2, result3 = self.map_parser.get_file_info("SWintegration_FD.c") #v2g_vehToGrid.c
        show(result1,result2,result3)

    def test_mode(self):

        link_result_df = self.map_parser.get_link_result_by_file_name("Adc.c") # bos
        # link_result_df = self.map_parser.get_link_result_by_file_name("SWintegration_FD.c") # dolu
        # link_result_df = self.map_parser.get_link_result_by_file_name("adc_analogInput.c") # dolu
        # link_result_df = self.map_parser.get_link_result_by_file_name("adc_analogInput_data.c") # full 
        # link_result_df = self.map_parser.get_link_result_by_file_name("cap_canApi.c") # bos
        # link_result_df = self.map_parser.get_link_result_by_file_name("cap_canApi_data.c") # bos
        matched_sections_df, matched_link_result_df, not_matched_link_result_df = self.map_parser.match_link_result_and_sections(link_result_df)
        matched_combined_sections_df, matched_last_link_result_df, not_matched_last_link_result_df = self.map_parser.match_link_result_and_combined_sections(not_matched_link_result_df)


        matched_sections_df = matched_sections_df.rename(columns={"Section": "[in] Section"})
        matched_sections_df = matched_sections_df.drop(columns=['Chip addr', 'Alignment', 'Size (MAU)'])
        # matched_link_result_df = matched_link_result_df.rename(columns={"[in] Section": "Section"})
        merged_link_result_and_sections = pd.merge(matched_link_result_df, matched_sections_df, on='[in] Section')

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

        show(not_matched_last_link_result_df) if not_matched_last_link_result_df.shape[0] != 0 else None

        # print("\n------------------")
        # print(merged_link_result_and_sections.shape[0])

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

    def test_the_test(self):
        dsram0_sum, dsram1_sum, dsram2_sum, dsram3_sum, dsram4_sum, dsram5_sum = 0, 0, 0, 0, 0, 0
        pfls0_sum, pfls1_sum, pfls2_sum, pfls3_sum = 0, 0, 0, 0
        self.map_parser.init_tables(["processed_files"])
        processed_files_df = self.map_parser.tables["processed_files"]
        for index, row in processed_files_df.iterrows():
            # self.test_mode_5(row)
            dsram0, dsram1, dsram2, dsram3, dsram4, dsram5, pfls0, pfls1, pfls2, pfls3 = self.test_mode_6(row["File"])
            dsram0_sum += dsram0
            dsram1_sum += dsram1
            dsram2_sum += dsram2
            dsram3_sum += dsram3
            dsram4_sum += dsram4
            dsram5_sum += dsram5
            pfls0_sum += pfls0
            pfls1_sum += pfls1
            pfls2_sum += pfls2
            pfls3_sum += pfls3
        print("dsram0: ", dsram0_sum)
        print("dsram1: ", dsram1_sum)
        print("dsram2: ", dsram2_sum)
        print("dsram3: ", dsram3_sum)
        print("dsram4: ", dsram4_sum)
        print("dsram5: ", dsram5_sum)
        print("pfls0: ", pfls0_sum)
        print("pfls1: ", pfls1_sum)
        print("pfls2: ", pfls2_sum)
        print("pfls3: ", pfls3_sum)

    def calc_actual_size(self, size_mau, alignment):
       return size_mau.apply(lambda x: int(x, 16)) + (size_mau.apply(lambda x: int(x, 16)) % alignment.apply(lambda x: int(x, 16)))

    def test_mode_5(self):

        # file_name = "pwm_pwmInputOutput_data.c" 
        # file_name = "Adc.c" # bos var combined var
        # file_name = "SWintegration_FD.c" #bos yok
        # file_name = "adc_analogInput.c" # bos yok
        # file_name = "adc_analogInput_data.c" # bos yok
        # file_name = "cap_canApi.c" # bos var
        # file_name = "cap_canApi_data.c" # bos var
        file_name = "ElapsedTime.o" # bos var combined var
        # file_name = "SuspendOSInterrupts.o" # bos var combined var


        link_result_df = self.map_parser.get_link_result_by_file_name(file_name)

        link_result_df_for_sec = link_result_df[['[in] File', '[in] Section', '[out] Section']]

        self.map_parser.init_tables(["locate_result_sections"])
        locate_result_sections_df = self.map_parser.tables["locate_result_sections"][['Chip', 'Section', 'Size (MAU)', 'Space addr', 'Alignment']]

        locate_result_sections_df_renamed = locate_result_sections_df.rename(columns={"Section" : "[out] Section"})
        merged_link_res_and_sec = pd.merge(link_result_df_for_sec, locate_result_sections_df_renamed, on='[out] Section', how='inner')

        self.map_parser.init_tables(["locate_result_combined_sections"])
        locate_result_combined_sections_df = self.map_parser.tables["locate_result_combined_sections"]

        link_result_df_for_comb_sec = link_result_df[['[in] File', '[out] Section']]
        link_result_df_for_comb_sec = link_result_df_for_comb_sec.rename(columns={"[out] Section": "[in] Section"})
        merged_link_res_and_combined_sec = pd.merge(link_result_df_for_comb_sec, locate_result_combined_sections_df, on='[in] Section', how='inner')

        merged_link_res_and_combined_sec['Chip'] = merged_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Chip'].values[0] if x in locate_result_sections_df['Section'].values else '')
        merged_link_res_and_combined_sec['Group addr'] = merged_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Space addr'].values[0] if x in locate_result_sections_df['Section'].values else '')

        merged_link_res_and_combined_sec['Space addr'] = merged_link_res_and_combined_sec.apply(lambda row: '0x' + hex(int(row['Space addr'], 16) + int(row['[out] Offset'], 16))[2:].zfill(8), axis=1)

        file_type_df = self.map_parser.get_file_type()

        # bunu ben nasıl yazdımmmmm
        self.map_parser.init_tables(["processed_files"])
        processed_files_df = self.map_parser.tables["processed_files"]
        merged_link_res_and_sec['File Type'] = merged_link_res_and_sec['[in] File'].apply(lambda x: file_type_df.loc[file_type_df['file_name'] == x, 'type'].values[0] 
                                                                                          if x in file_type_df['file_name'].values
                                                                                          else file_type_df.loc[file_type_df['file_name'] == processed_files_df.loc[processed_files_df['File'] == x, 'From archive'].values[0], 'type'].values[0]+', from archive file: '+file_type_df.loc[file_type_df['file_name'] == processed_files_df.loc[processed_files_df['File'] == x, 'From archive'].values[0], 'file_name'].values[0] if x in processed_files_df['File'].values 
                                                                                          else 'NotFounded')

        # merged_link_res_and_combined_sec['File Type'] = merged_link_res_and_combined_sec['[in] File'].apply(lambda x: file_type_df.loc[file_type_df['file_name'] == x, 'type'].values[0] 
        #                                                                                                     if x in file_type_df['file_name'].values 
        #                                                                                                     else file_type_df.loc[file_type_df['file_name'] == processed_files_df.loc[processed_files_df['File'] == x, 'From archive'].values[0], 'type'].values[0]+', from archive file: '+file_type_df.loc[file_type_df['file_name'] == processed_files_df.loc[processed_files_df['File'] == x, 'From archive'].values[0], 'file_name'].values[0] if x in processed_files_df['File'].values 
        #                                                                                                     else 'NotFounded')

        sum_value_link_res_sec  = merged_link_res_and_sec['Size (MAU)'].apply(lambda x: int(x, 16)).sum()
        merged_link_res_and_sec["Chip Size"] = self.calc_actual_size(merged_link_res_and_sec['Size (MAU)'], merged_link_res_and_sec["Alignment"])
        # sum_value_link_comb_res_sec  = merged_link_res_and_combined_sec['[in] Size (MAU)'].apply(lambda x: int(x, 16)).sum()
        show(merged_link_res_and_sec)
        size_df = pd.DataFrame({'From': ['merged_link_res_and_sec', 'merged_link_res_and_combined_sec'],
                           'Size': [sum_value_link_res_sec, 0]})

        sum_actual = merged_link_res_and_sec["Chip Size"].sum()
        print("sum_actual: ", sum_actual)

        # TODO: debug printi bulunamadığında print at
        not_found_pd_df = self.map_parser.get_not_found_symbol(file_name)

        MapFileTable().save_df_as(merged_link_res_and_sec, file_name + "_merged_link_res_and_sec", "html")
        # MapFileTable().save_df_as(merged_link_res_and_combined_sec, file_name + "_merged_link_res_and_combined_sec", "html")
        MapFileTable().save_df_as(size_df, file_name + "_size_df", "html")
        MapFileTable().save_df_as(not_found_pd_df, file_name + "_not_founded_symbols", "html")
        
        print("bir: ", sum_value_link_res_sec)
        # print("iki: ", sum_value_link_comb_res_sec)
        
        dsram0_size, dsram1_size, dsram2_size, dsram3_size, dsram4_size, dsram5_size = 0, 0, 0, 0, 0, 0
        pfls0_size, pfls1_size, pfls2_size, pfls3_size = 0, 0, 0, 0

        grouped_df = merged_link_res_and_sec.groupby("Chip")
        # grouped_df = merged_link_res_and_combined_sec.groupby("Chip")
        search_key_sec = 'Size (MAU)'
        for key, item in grouped_df:

            if key == 'mpe:dsram0':
                dsram0_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram1':
                dsram1_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram2':
                dsram2_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram3':
                dsram3_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram4':
                dsram4_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram5':
                dsram5_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()
                
            if key == 'mpe:pfls0':
                pfls0_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls1':
                pfls1_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls2':
                pfls2_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls3':
                pfls3_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()
        print("dsram1:", dsram1_size)
        print("plfs0:", pfls0_size)
        show(merged_link_res_and_sec, size_df, not_found_pd_df)

    def test_mode_6(self, file_name):

        link_result_df = self.map_parser.get_link_result_by_file_name(file_name)

        link_result_df_for_sec = link_result_df[['[in] File', '[in] Section', '[out] Section']]
        
        self.map_parser.init_tables(["locate_result_sections"])
        locate_result_sections_df = self.map_parser.tables["locate_result_sections"][['Chip', 'Section', 'Size (MAU)', 'Chip addr']]

        locate_result_sections_df_renamed = locate_result_sections_df.rename(columns={"Section" : "[out] Section"})
        merged_link_res_and_sec = pd.merge(link_result_df_for_sec, locate_result_sections_df_renamed, on='[out] Section', how='inner')

        self.map_parser.init_tables(["locate_result_combined_sections"])
        locate_result_combined_sections_df = self.map_parser.tables["locate_result_combined_sections"]

        link_result_df_for_comb_sec = link_result_df[['[in] File', '[out] Section']]
        link_result_df_for_comb_sec = link_result_df_for_comb_sec.rename(columns={"[out] Section": "[in] Section"})
        merged_link_res_and_combined_sec = pd.merge(link_result_df_for_comb_sec, locate_result_combined_sections_df, on='[in] Section', how='inner')

        merged_link_res_and_combined_sec['Chip'] = merged_link_res_and_combined_sec['[out] Section'].apply(lambda x: locate_result_sections_df.loc[locate_result_sections_df['Section'] == x, 'Chip'].values[0] if x in locate_result_sections_df['Section'].values else '')

        dsram0_size, dsram1_size, dsram2_size, dsram3_size, dsram4_size, dsram5_size = 0, 0, 0, 0, 0, 0
        pfls0_size, pfls1_size, pfls2_size, pfls3_size = 0, 0, 0, 0

        grouped_df = merged_link_res_and_sec.groupby("Chip")
        # grouped_df = merged_link_res_and_combined_sec.groupby("Chip")
        search_key_sec = 'Size (MAU)'
        search_key_comb_sec = '[in] Size (MAU)'
        for key, item in grouped_df:

            if key == 'mpe:dsram0':
                dsram0_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram1':
                dsram1_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram2':
                dsram2_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram3':
                dsram3_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram4':
                dsram4_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram5':
                dsram5_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()
                
            if key == 'mpe:pfls0':
                pfls0_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls1':
                pfls1_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls2':
                pfls2_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls3':
                pfls3_size += grouped_df.get_group(key)[search_key_sec].apply(lambda x: int(x, 16)).sum()

        return dsram0_size, dsram1_size, dsram2_size, dsram3_size, dsram4_size, dsram5_size, pfls0_size, pfls1_size, pfls2_size, pfls3_size
    
    def test_sections_df(self):
        self.map_parser.init_tables(["locate_result_sections"])
        sec_df = self.map_parser.tables["locate_result_sections"]
        sec_grouped_df = sec_df.groupby("Chip")
        dsram0_size, dsram1_size, dsram2_size, dsram3_size, dsram4_size, dsram5_size = 0, 0, 0, 0, 0, 0
        pfls0_size, pfls1_size, pfls2_size, pfls3_size = 0, 0, 0, 0

        for key, item in sec_grouped_df:

            if key == 'mpe:dsram0':
                dsram0_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram1':
                dsram1_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram2':
                dsram2_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram3':
                dsram3_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram4':
                dsram4_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:dsram5':
                dsram5_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()
                
            if key == 'mpe:pfls0':
                pfls0_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls1':
                pfls1_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls2':
                pfls2_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

            if key == 'mpe:pfls3':
                pfls3_size += sec_grouped_df.get_group(key)['Size (MAU)'].apply(lambda x: int(x, 16)).sum()

        print("dsram0: ", dsram0_size)
        print("dsram1: ", dsram1_size)
        print("dsram2: ", dsram2_size)
        print("dsram3: ", dsram3_size)
        print("dsram4: ", dsram4_size)
        print("dsram5: ", dsram5_size)
        print("pfls0: ", pfls0_size)
        print("pfls1: ", pfls1_size)
        print("pfls2: ", pfls2_size)
        print("pfls3: ", pfls3_size)

    def test_for_meeting(self):
        self.map_parser.init_tables(["all"])
        print("aa")
        print("bb")

if __name__ == '__main__':
    unittest.main()