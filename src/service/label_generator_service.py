from typing import List, Tuple

class LabelGenerator:
    def generate_zpl(self, eans_and_skus: List[Tuple[str, str, int]], label_format: str) -> str:
        if not label_format:
            raise ValueError("Formato de etiqueta não pode ser nulo ou vazio.")

        label_generators = {
            "1-Coluna": self.generate_zpl_1_column,
            "2-Colunas": self.generate_zpl_2_columns,
            "QRCode": self.generate_zpl_qrcode,
            "Code128": self.generate_zpl_code128,
            "Ambos": self.generate_zpl_and_sku_ean
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
                    self.append_both_label(zpl, ean, sku)
                elif sku:
                    self.generate_sku(zpl, sku)
                elif ean:
                    self.generate_ean(zpl, ean)

                zpl.append("^XZ")

        return "\n".join(zpl)

    def append_both_label(self, zpl: list, ean: str, sku: str) -> None:
        zpl.append(f"^LH0,0\n^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        zpl.append(f"^FO45,168^A0N,20,20^FDSKU: {sku}^FS")
        zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        zpl.append(f"^FO440,168^A0N,20,20^FDSKU: {sku}^FS")

    def generate_ean(self, zpl: list, ean: str) -> None:
        zpl.extend([
            f"^LH0,0\n^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS",
            f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS"
        ])

    def generate_sku(self, zpl: list, sku: str) -> None:
        typebarcode = "BCN"
        zpl.extend([
            f"^LH0,0\n^FO65,18^BY2,,0^{typebarcode},54,N,N^FD{sku}^FS",
            f"^FO145,80^A0N,20,28^FH^FD{sku}^FS",
            f"^FO146,80^A0N,20,28^FH^FD{sku}^FS",
            f"^FS\n^CI28\n^LH0,0\n^FO475,18^BY2,,0^{typebarcode},54,N,N^FD{sku}^FS",
            f"^FO555,80^A0N,20,28^FH^FD{sku}^FS",
            f"^FO556,80^A0N,20,28^FH^FD{sku}^FS\n^FS"
        ])

    def generate_zpl_1_column(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl.append("^XA^CI28")
                zpl.append("^PW800")
                zpl.append("^LL200")
                if ean:
                    zpl.append(self.generate_barcode(ean))
                if sku:
                    zpl.append(self.generate_barcode(sku))
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_barcode(self, data: str) -> str:
        return f"^BY2,,0^BCN,54,N,N^FD{data}^FS^XZ"

    def generate_zpl_default(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        return "^XA^FO50,50^GB500,500,500^FS^XZ"

    def generate_zpl_code128(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if sku:
                    zpl.append(f"^BY2,,0^BCN,54,N,N^FD{sku}^FS")
                elif ean:
                    zpl.append(f"^BY2,,0^BEN,54,Y,N^FD{ean}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_code39(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if sku:
                    zpl.append(f"^BY2,,0^B3N,50,Y,N^FD{sku}^FS")
                elif ean:
                    zpl.append(f"^BY2,,0^BEN,54,Y,N^FD{ean}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_ean13(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if ean:
                    zpl.append(f"^BY2,,0^BEN,54,Y,N^FD{ean}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)
    
    def generate_zpl_and_sku_ean(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []

        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if ean:
                    zpl.append(f"^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
                    zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
                if sku:
                    zpl.append(f"^FO440,168^A0N,20,20^FDSKU: {sku}^FS")
                zpl.append("^XZ")

        return "\n".join(zpl)

    def generate_zpl_upc_a(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if sku:
                    zpl.append(f"^BY2,,0^BU,54,Y,N^FD{sku}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_qrcode(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                if ean:
                    zpl.append(f"^FO475,35^BY3,80,Y^FDMA,100,Y^FD{ean}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)
