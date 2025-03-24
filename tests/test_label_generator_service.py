import unittest
from src.service.generator.label_generator_service import LabelGenerator

class TestLabelGenerator(unittest.TestCase):
    def setUp(self):
        self.label_generator = LabelGenerator(label_format="1-Coluna")

    def test_generate_zpl_1_column(self):
        eans_and_skus = [("1234567890123", "SKU123", 2)]
        zpl = self.label_generator.generate_zpl(eans_and_skus, "1-Coluna")
        self.assertIn("^XA^CI28", zpl)
        self.assertIn("^XZ", zpl)

    def test_generate_zpl_2_columns(self):
        eans_and_skus = [("1234567890123", "SKU123", 2)]
        zpl = self.label_generator.generate_zpl(eans_and_skus, "2-Colunas")
        self.assertIn("^XA^CI28", zpl)
        self.assertIn("^XZ", zpl)

    def test_invalid_label_format(self):
        eans_and_skus = [("1234567890123", "SKU123", 2)]
        with self.assertRaises(ValueError):
            self.label_generator.generate_zpl(eans_and_skus, "Invalid-Format")

if __name__ == "__main__":
    unittest.main()
