from typing import List, Tuple

class LabelGenerator:
    TYPEBARCODES = {"BEN", "BCN", "B3N", "BU", "FDMA"}

    def generate_zpl(self, eans_and_skus: List[Tuple[str, str, int]], label_format: str) -> str:
        if not label_format:
            raise ValueError("Formato de etiqueta não pode ser nulo ou vazio.")

        label_generators = {
            "1-Coluna": self.generate_zpl_1_column,
            "2-Colunas": self.generate_zpl_2_columns,
            "4-etiquetas por página": self.generate_zpl_4_labels_per_page,
            "QRCode": self.generate_zpl_qrcode,
            "Code128": self.generate_zpl_code128
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
                if sku:
                    self.generate_sku(zpl, sku)
                elif ean:
                    self.generate_ean(zpl, ean)
                zpl.append("^XZ")
    
            return "\n".join(zpl)

    def generate_ean(self, zpl: list, ean: str) -> None:
        zpl.extend([
            "^PW800", "^LL200", "^CI28", "^LH0,0",
            f"^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS",
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
                if ean:
                    zpl.append(self.generate_barcode(ean))
                if sku:
                    zpl.append(self.generate_barcode(sku))
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_4_labels_per_page(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        
        for ean, sku, quantity in eans_and_skus:
            adjusted_quantity = math.ceil(quantity / 4) * 4
            
            for _ in range(adjusted_quantity // 4):
                zpl.append(f"^XA\n^FO50,50\n^BQN,2,10\n^FDMA,{ean}^FS\n"
                        f"\n^FO400,50\n^BQN,2,10\n^FDMA,{ean}^FS\n"
                        f"\n^FO50,400\n^BQN,2,10\n^FDMA,{ean}^FS\n"
                        f"\n^FO400,400\n^BQN,2,10\n^FDMA,{ean}^FS\n"
                        f"\n^XZ")
        return "\n".join(zpl)

    def generate_barcode(self, data: str) -> str:
        return f"^BY2,,0^BCN,54,N,N^FD{data}^FS^XZ"

    def generate_zpl_default(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        return "^XA^FO50,50^GB500,500,500^FS^XZ"

    def generate_zpl_code128(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl.append("^XA")
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
                zpl.append("^XA")
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
                zpl.append("^XA")
                if ean:
                    zpl.append(f"^BY2,,0^BEN,54,Y,N^FD{ean}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_upc_a(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl.append("^XA")
                if sku:
                    zpl.append(f"^BY2,,0^BU,54,Y,N^FD{sku}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)

    def generate_zpl_qrcode(self, eans_and_skus: List[Tuple[str, str, int]]) -> str:
        zpl = []
        for ean, sku, quantity in eans_and_skus:
            for _ in range(quantity):
                zpl.append("^XA")
                if ean:
                    zpl.append(f"^BQN,2,10^FDMA,{ean}^FS")
                zpl.append("^XZ")
        return "\n".join(zpl)
