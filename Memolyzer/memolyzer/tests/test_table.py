import unittest
from memolyzer.table import MapFileTable

row = ["mpe:dsram0", ".bss.VCU_VehicleHVStatus_CHS2.ClearedData.Cpu0.Unspecified(1340)", "0x00000001" ,"0x7003a6a4", "0x0003a6a4", "0x00000004"]
class TestMapParser(unittest.TestCase):
    map_file_table = MapFileTable()

    def test_type_fit(self):
        merged_row = self.map_file_table.type_fit(row)
        print(merged_row)


if __name__ == '__main__':
    unittest.main()