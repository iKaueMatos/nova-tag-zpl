import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.infra.sheet import SheetImporter

class TestSheetImporter(unittest.TestCase):
    def setUp(self):
        self.generator = MagicMock()
        self.tree = MagicMock()
        self.importer = SheetImporter(self.generator, self.tree, "EAN")

    @patch("tkinter.filedialog.askopenfilename")
    @patch("pandas.read_csv")
    def test_import_sheet_csv(self, mock_read_csv, mock_askopenfilename):
        mock_askopenfilename.return_value = "test.csv"
        mock_read_csv.return_value = pd.DataFrame({"EAN": ["1234567890123"], "SKU": ["SKU123"], "Quantidade": [2]})
        self.importer.import_sheet()
        self.generator.add_ean_sku.assert_called_once_with(1234567890123, "SKU123", 2)

    @patch("tkinter.filedialog.askopenfilename")
    @patch("pandas.read_excel")
    def test_import_sheet_excel(self, mock_read_excel, mock_askopenfilename):
        mock_askopenfilename.return_value = "test.xlsx"
        mock_read_excel.return_value = pd.DataFrame({"EAN": ["1234567890123"], "SKU": ["SKU123"], "Quantidade": [2]})
        self.importer.import_sheet()
        self.generator.add_ean_sku.assert_called_once_with(1234567890123, "SKU123", 2)

if __name__ == "__main__":
    unittest.main()
