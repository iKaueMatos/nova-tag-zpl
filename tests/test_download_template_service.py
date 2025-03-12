import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from src.service.download_template_service import TemplateDownloadService

class TestTemplateDownloadService(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.service = TemplateDownloadService(self.root)

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("pandas.DataFrame.to_csv")
    def test_download_template_ean(self, mock_to_csv, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value = "test.csv"
        self.service.template_type = tk.StringVar(value="EAN")
        self.service.download_template()
        mock_to_csv.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("pandas.DataFrame.to_csv")
    def test_download_template_sku(self, mock_to_csv, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value = "test.csv"
        self.service.template_type = tk.StringVar(value="SKU")
        self.service.download_template()
        mock_to_csv.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("pandas.DataFrame.to_csv")
    def test_download_template_ambos(self, mock_to_csv, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value = "test.csv"
        self.service.template_type = tk.StringVar(value="Ambos")
        self.service.download_template()
        mock_to_csv.assert_called_once()

if __name__ == "__main__":
    unittest.main()
