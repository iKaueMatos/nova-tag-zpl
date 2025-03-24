import unittest
from unittest.mock import patch
import tkinter as tk
from src.views.barcode.barcode_screen import BarcodeScreen

class TestBarcodeLabelApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = BarcodeScreen(self.root)

    @patch("tkinter.filedialog.askopenfilename")
    def test_import_sheet(self, mock_askopenfilename):
        mock_askopenfilename.return_value = "test.csv"
        self.app.import_sheet()
        self.app.importer.import_sheet.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_save_zpl(self, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value = "test.zpl"
        self.app.zpl_code = "ZPL_CODE"
        self.app.save_zpl()
        with open("test.zpl", "r") as file:
            content = file.read()
        self.assertEqual(content, "ZPL_CODE")

    def test_clear_data(self):
        self.app.tree.insert("", "end", values=("1234567890123", "SKU123", 2))
        self.app.clear_data()
        self.assertEqual(len(self.app.tree.get_children()), 0)

if __name__ == "__main__":
    unittest.main()
