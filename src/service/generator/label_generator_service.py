from typing import List, Union

from src.models.Label_item import LabelItem
from src.service.generator.type_model_tag_service import TypeModelTagService

class LabelGenerator:
    def __init__(self, label_format: str, model_tag: str):
        self.type_model_tag_service = TypeModelTagService()
        self.label_format = label_format

    def generate_zpl(self, eans_and_skus: List[Union[LabelItem, tuple]], label_format: str = None,
                     model_tag=None) -> str:
        def sanitize_value(value):
            """ Substitui valores vazios ('', '-') por None """
            return None if value in ["", "-"] else value

        def create_label_item(item):
            if isinstance(item, LabelItem):
                return item
            elif isinstance(item, tuple):
                ean, sku, quantity, description, *optional = item
                code, size = (optional + ["", ""])[:2]

                return LabelItem(
                    sanitize_value(ean),
                    sanitize_value(sku),
                    sanitize_value(quantity),
                    sanitize_value(description),
                    sanitize_value(code),
                    sanitize_value(size)
                )
            else:
                raise ValueError(f"Formato inválido para item: {item}")

        eans_and_skus = [create_label_item(item) for item in eans_and_skus]
        label_format = label_format or self.label_format

        if not label_format:
            raise ValueError("Formato de etiqueta não pode ser nulo ou vazio.")

        label_generators = {
            "1-Coluna": self.generate_zpl_1_column,
            "2-Colunas": self.generate_zpl_2_columns,
        }

        if label_format not in label_generators:
            raise ValueError("Formato de etiqueta desconhecido.")

        return label_generators[label_format](eans_and_skus, model_tag)

    def generate_zpl_2_columns(self, eans_and_skus: List[LabelItem], model_tag) -> str:
        zpl = []

        for item in eans_and_skus:
            adjusted_quantity = item.quantity if item.quantity % 2 == 0 else item.quantity + 1

            for _ in range(adjusted_quantity // 2):
                zpl.append("^XA^CI28")
                zpl.append("^PW800")
                zpl.append("^LL200")

                if model_tag == "Full Mercado Livre":
                    self.type_model_tag_service.generate_code_128_full_mercado_livre(zpl, item.code, item.sku,
                                                                                     item.description, item.size,
                                                                                     self.label_format)
                elif model_tag == "Full Amazon":
                    self.type_model_tag_service.generate_code_128_full_amazon(zpl, item.code, item.sku,
                                                                              item.description, self.label_format)
                elif model_tag == "Ambos(EAN e SKU)":
                    self.type_model_tag_service.append_both_label(zpl, item.ean, item.sku, self.label_format)
                elif model_tag == "EAN":
                    self.type_model_tag_service.generate_ean(zpl, item.ean, self.label_format)
                elif model_tag == "SKU":
                    self.type_model_tag_service.generate_code_128(zpl, item.sku, self.label_format)

                zpl.append("^XZ")

        return "\n".join(zpl)

    def generate_zpl_1_column(self, eans_and_skus: List[LabelItem], model_tag) -> str:
        zpl = []

        for item in eans_and_skus:
            for _ in range(item.quantity):
                zpl.append("^XA^CI28")
                zpl.append("^PW800")
                zpl.append("^LL300")

                if model_tag == "Full Mercado Livre":
                    self.type_model_tag_service.generate_code_128_full_mercado_livre(zpl, item.code, item.sku,
                                                                                     item.description, item.size,
                                                                                     self.label_format)
                elif model_tag == "Full Amazon":
                    self.type_model_tag_service.generate_code_128_full_amazon(zpl, item.code, item.sku,
                                                                              item.description, self.label_format)
                elif model_tag == "Ambos(EAN e SKU)":
                    self.type_model_tag_service.append_both_label(zpl, item.ean, item.sku, self.label_format)
                elif model_tag == "EAN":
                    self.type_model_tag_service.generate_ean(zpl, item.ean, self.label_format)
                elif model_tag == "SKU":
                    self.type_model_tag_service.generate_code_128(zpl, item.sku, self.label_format)

                zpl.append("^XZ")

        return "\n".join(zpl)