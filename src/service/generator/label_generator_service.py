from typing import List, Tuple

from src.service.generator.type_model_tag_service import TypeModelTagService


class LabelGenerator:
    def __init__(self, label_format: str):  # Valor padrão definido
        self.type_model_tag_service = TypeModelTagService()
        self.label_format = label_format

    def generate_zpl(self, eans_and_skus: List[Tuple[str, str, int]], label_format: str = None) -> str:
        label_format = label_format or self.label_format

        if not label_format:
            raise ValueError("Formato de etiqueta não pode ser nulo ou vazio.")

        label_generators = {
            "1-Coluna": self.generate_zpl_1_column,
            "2-Colunas": self.generate_zpl_2_columns,
        }

        if label_format not in label_generators:
            raise ValueError("Formato de etiqueta desconhecido.")

        return label_generators[label_format](eans_and_skus)

    def generate_zpl_2_columns(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []

        for ean, sku, quantity in eans_and_skus:
            adjusted_quantity = quantity if quantity % 2 == 0 else quantity + 1

            for _ in range(adjusted_quantity // 2):
                zpl.append("^XA^CI28")
                zpl.append("^PW800")
                zpl.append("^LL200")

                if sku and ean:
                    self.type_model_tag_service.append_both_label(zpl, ean, sku)
                elif sku:
                    self.type_model_tag_service.generate_code_128(zpl, sku, self.label_format)
                elif ean:
                    self.type_model_tag_service.generate_ean(zpl, ean, self.label_format)

                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_1_column(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl.append("^XA^CI28")
                zpl.append("^PW800")
                zpl.append("^LL300")

                if ean:
                    self.type_model_tag_service.generate_ean(zpl, ean, self.label_format)
                if sku:
                    self.type_model_tag_service.generate_code_128(zpl, sku, self.label_format)
                zpl.append("^XZ")

        zpl = [item for item in zpl if item is not None]
        return "\n".join(zpl)
