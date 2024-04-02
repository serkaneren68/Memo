from memolyzer.map_parser import MapParser
from memolyzer.cli import Cli

temp_modes = {"symbol_info":None,
              "file_info": None,
              "overall": None,
              "specific_mem_usage": None,
              "mem_section_with_check": None,
              "get_table_from_map_file": None
              }

class Modes():
    def __init__(self) -> None:
        self.args = Cli().get_args()
        self.map_parser = MapParser()
        self.modes = temp_modes
        
    def run_modes(self):

        mode_functions = {"symbol_info":self.map_parser.get_symbol_info, # tamamlandı
                          "overall": self.map_parser.init_overall, # percentage yazdırılacak
                          "specific_mem_usage": None, # tek bir satırı döndürecek mesela dsrame göre # apply copy yada query bak

                          # test_mode_5 kullan
                          # excelin her satırı için passed yada failed
                          # eğer ki satır failse (expected içerisinde olmayan sembol, memory e.g. dsram1, ama bu expected da yok şeklinde string döndürecek) 
                          "mem_section_with_check": None,  # excel den birden fazla alacak

                          # test_mode_5 kullan
                          "file_info": self.map_parser.get_file_info, # section, Referenced in çıkar, symbol gelicek size tablosu
                          # sorted on symbols de ara symbolu bul, size ve address yazdır

                          "get_table_from_map_file": None # tabloları döndürecek
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