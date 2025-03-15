import unittest
from unittest.mock import patch
from src.service.zebra.zebra_printer_service import ZebraPrinterService

class TestZebraPrinterService(unittest.TestCase):
    def setUp(self):
        self.printer_service = ZebraPrinterService()

    @patch("zebra.Zebra.getqueues")
    def test_get_printers(self, mock_getqueues):
        mock_getqueues.return_value = ["Printer1", "Printer2"]
        printers = self.printer_service.get_printers()
        self.assertEqual(printers, ["Printer1", "Printer2"])

    @patch("zebra.Zebra.output")
    def test_print_label(self, mock_output):
        self.printer_service.print_label("ZPL_CODE")
        mock_output.assert_called_once_with("ZPL_CODE")

    @patch("os.system")
    def test_clear_print_queue(self, mock_system):
        self.printer_service.clear_print_queue()
        self.assertEqual(mock_system.call_count, 3)

if __name__ == "__main__":
    unittest.main()
