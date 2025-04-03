# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
class TypeModelTagService:
    def generate_ean(self, zpl: list, ean: str, label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append("^LH0,0")
            zpl.append(f"^FO260,40^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        elif label_format == "2-Colunas":
            zpl.append("^LH0,0")
            zpl.append(f"^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
            zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
        else:
            raise ValueError(f"Formato de etiqueta desconhecido: {label_format}")

    def generate_code_128(self, zpl: list, sku: str, label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append("^LH0,0")
            zpl.append(f"^FO180,65^BY4,80,Y^BCN,100,Y^FD{sku}^FS")
        elif label_format == "2-Colunas":
            zpl.append("^LH0,0")
            zpl.append(f"^FO55,50^BY3,60,Y^BCN,80,Y^FD{sku}^FS")
            zpl.append(f"^FO455,50^BY3,60,Y^BCN,80,Y^FD{sku}^FS")
        else:
            raise ValueError(f"Formato de etiqueta desconhecido: {label_format}")

    def append_both_label(self, zpl: list, ean: str, sku: str, label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append("^LH0,0")
            zpl.append(f"^FO190,45^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
            zpl.append(f"^FO155,180^A0N,20,20^FDSKU: {sku}^FS")
        if label_format == "2-Colunas":
            zpl.append("^LH0,0")
            zpl.append(f"^FO80,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
            zpl.append(f"^FO45,168^A0N,20,20^FDSKU: {sku}^FS")
            zpl.append(f"^FO475,35^BY3,80,Y^BEN,100,Y^FD{ean}^FS")
            zpl.append(f"^FO440,168^A0N,20,20^FDSKU: {sku}^FS")

    def generate_code_128_full_mercado_livre(self, zpl: list, code: str, sku: str, description: str, size: str, label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append("^LH0,0")
            zpl.append(f"^FO290,18^BY2,,0^BCN,54,N,N^FD{code}^FS")
            zpl.append(f"^FO375,80^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO375,80^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO290,115^A0N,18,18^FB380,2,0,L^FH^FD{description}^FS")
            zpl.append(f"^FO290,150^A0N,18,18^FB380,1,0,L^FH^FD{size}^FS")
            zpl.append(f"^FO290,150^A0N,18,18^FB380,1,0,L^FH^FD{size}^FS")
            zpl.append(f"^FO290,170^A0N,18,18^FH^FDSKU: {sku}^FS")
        elif label_format == "2-Colunas":

            # Coluna da esquerda
            zpl.append("^LH0,0")
            zpl.append(f"^FO65,18^BY2,,0^BCN,54,N,N^FD{code}^FS")
            zpl.append(f"^FO145,80^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO146,80^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO22,115^A0N,18,18^FB380,2,0,L^FH^FD{description}^FS")
            zpl.append(f"^FO22,150^A0N,18,18^FB380,1,0,L^FH^FD{size}^FS")
            zpl.append(f"^FO21,150^A0N,18,18^FB380,1,0,L^FH^FD{size}^FS")
            zpl.append(f"^FO22,170^A0N,18,18^FH^FDSKU: {sku}^FS")

            # Coluna da direita
            zpl.append("^LH0,0")
            zpl.append(f"^FO475,18^BY2,,0^BCN,54,N,N^FD{code}^FS")
            zpl.append(f"^FO555,80^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO556,80^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO432,115^A0N,18,18^FB380,2,0,L^FH^FD{description}^FS")
            zpl.append(f"^FO432,150^A0N,18,18^FB380,1,0,L^FH^FD{size}^FS")
            zpl.append(f"^FO431,150^A0N,18,18^FB380,1,0,L^FH^FD{size}^FS")
            zpl.append(f"^FO432,170^A0N,18,18^FH^FDSKU: {sku}^FS")

    def generate_code_128_full_amazon(self, zpl: list, code: str, sku: str, description: str,
                                             label_format: str) -> None:
        if label_format == "1-Coluna":
            zpl.append("^LH0,0")
            zpl.append(f"^FO290,18^BY2,,0^BCN,54,N,N^FD{code}^FS")  # Código de barras
            zpl.append(f"^FO365,85^A0N,20,25^FH^FD{code}^FS")  # Código como texto
            zpl.append(f"^FO365,115^A0N,18,18^FB380,2,0,L^FH^FD{description}^FS")  # Descrição do produto
            zpl.append(f"^FO290,170^A0N,18,18^FH^FDSKU: {sku}^FS")  # SKU

        elif label_format == "2-Colunas":
            # Coluna da esquerda
            zpl.append("^LH0,0")
            zpl.append(f"^FO62,18^BY2,,0^BCN,54,N,N^FD{code}^FS")
            zpl.append(f"^FO143,85^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO143,115^A0N,18,18^FB380,2,0,L^FH^FD{description}^FS")
            zpl.append(f"^FO22,170^A0N,18,18^FH^FDSKU: {sku}^FS")

            # Coluna da direita
            zpl.append("^LH0,0")
            zpl.append(f"^FO472,18^BY2,,0^BCN,54,N,N^FD{code}^FS")
            zpl.append(f"^FO552,85^A0N,20,25^FH^FD{code}^FS")
            zpl.append(f"^FO549,115^A0N,18,18^FB380,2,0,L^FH^FD{description}^FS")
            zpl.append(f"^FO432,170^A0N,18,18^FH^FDSKU: {sku}^FS")