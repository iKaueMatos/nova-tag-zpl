from .label_generator import LabelGenerator

class BarcodeLabelGenerator:
    def __init__(self):
        self.eans_and_skus = []
        self.label_format = "2 Colunas"  # Default label format
        self.label_generator = LabelGenerator()

    @staticmethod
    def validate_ean(ean):
        if not ean.isdigit() or len(ean) not in [8, 12, 13, 14]:
            return False

        reverse_digits = list(map(int, reversed(ean)))
        checksum = sum(reverse_digits[0::2]) + sum(d * 3 for d in reverse_digits[1::2])
        return checksum % 10 == 0

    def add_ean_sku(self, ean, sku, quantity):
        self.eans_and_skus.append((ean, sku, quantity))

    def set_label_format(self, format_name):
        self.label_format = format_name

    def generate_zpl(self):
        return self.label_generator.generate_zpl(self.eans_and_skus, self.label_format)

    def save_zpl_to_file(self, zpl_code, file_path):
        with open(file_path, "w") as zpl_file:
            zpl_file.write(zpl_code)
