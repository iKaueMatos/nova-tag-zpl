class TypeModelTagService:
    def generate_ean(self, zpl: list, ean: str, label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append(f"^FO180,65^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        elif label_format == "2-Colunas":
            zpl.append(f"^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
            zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        else:
            raise ValueError(f"Formato de etiqueta desconhecido: {label_format}")

    def generate_code_128(self, zpl: list, sku: str, label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append(f"^FO180,65^BY4,80,Y^BCN,100,Y^FD{sku}^FS")
        elif label_format == "2-Colunas":
            zpl.append(f"^FO55,50^BY3,60,Y^BCN,80,Y^FD{sku}^FS")
            zpl.append(f"^FO455,50^BY3,60,Y^BCN,80,Y^FD{sku}^FS")
        else:
            raise ValueError(f"Formato de etiqueta desconhecido: {label_format}")

    def append_both_label(self, zpl: list, ean: str, sku: str) -> None:
        zpl.append(f"^LH0,0\n^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        zpl.append(f"^FO45,168^A0N,20,20^FDSKU: {sku}^FS")
        zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        zpl.append(f"^FO440,168^A0N,20,20^FDSKU: {sku}^FS")