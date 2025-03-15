import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

from src.service.validation.ean_validator import EANValidator


class SheetImporterService:
    def __init__(self, generator, tree, code_type, label_format):
        self.generator = generator
        self.tree = tree
        self.code_type = code_type
        self.label_format = label_format

    def import_sheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("Planilhas", "*.csv *.xlsx *.xls *.ods")])
        if not file_path:
            return

        try:
            data = self._read_file(file_path)
            data = self._clean_and_validate_data(data)
            self._process_data(data)
            messagebox.showinfo("Sucesso", "Dados importados e tratados com sucesso!")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Erro", "O arquivo está vazio.")
        except pd.errors.ParserError:
            messagebox.showerror("Erro", "Erro ao ler o arquivo. Verifique o formato.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar planilha: {e}")

    def _read_file(self, file_path):
        """Lê o arquivo, tentando diferentes formatos e codificações se necessário."""
        try:
            if file_path.endswith(".csv"):
                try:
                    return pd.read_csv(file_path, encoding="utf-8")
                except UnicodeDecodeError:
                    return pd.read_csv(file_path, encoding="latin-1")

            elif file_path.endswith((".xlsx", ".xls")):
                return pd.read_excel(file_path)

            elif file_path.endswith(".ods"):
                return pd.read_excel(file_path, engine="odf")

            else:
                raise ValueError("Formato de arquivo não suportado!")

        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo: {e}")

    def _clean_and_validate_data(self, data):
        """
        Trata e valida os dados:
            - Converte EAN e Quantidade para números.
            - Garante que SKU seja tratado como string.
            - Substitui células vazias por '-'.
            - Remove linhas com dados inválidos.
        """
        data["EAN"] = data["EAN"].astype(str).str.replace(".0", "", regex=False)
        data["SKU"] = data["SKU"].astype(str).str.replace(".0", "", regex=False)

        data.loc[:, "EAN"] = data["EAN"].fillna("-")
        data.loc[:, "SKU"] = data["SKU"].fillna("-")
        data["Quantidade"] = pd.to_numeric(data["Quantidade"], errors="coerce", downcast="integer")
        data["Quantidade"] = data["Quantidade"].fillna(0).astype(int)
        data.loc[:, "Quantidade"] = data["Quantidade"].astype(str)

        data["EAN"] = pd.to_numeric(data["EAN"], errors="coerce", downcast="integer")
        data["Quantidade"] = pd.to_numeric(data["Quantidade"], errors="coerce", downcast="integer")

        data = data.dropna(subset=["EAN", "Quantidade"])
        data = data[data["EAN"] != 0]
        data = data[data["Quantidade"] != 0]
        data = data[data["SKU"].str.match(r"^[a-zA-Z0-9]+$")]

        duplicated = data[data.duplicated(["EAN", "SKU"], keep=False)]
        if not duplicated.empty:
            duplicates_list = duplicated.to_string(index=False)
            messagebox.showwarning("Aviso",
                                   f"Os seguintes EANs e SKUs foram desconsiderados por serem duplicados:\n{duplicates_list}")
            data = data.drop_duplicates(["EAN", "SKU"], keep='first')

        return data

    def _process_data(self, data):
        """
        Processa os dados tratados e os adiciona ao Treeview e ao gerador.
        """
        columns = data.columns

        if "EAN" in columns and "SKU" in columns:
            self.code_type.set("Ambos")
        elif "EAN" in columns:
            self.code_type.set("EAN")
        elif "SKU" in columns:
            self.code_type.set("SKU")
        else:
            messagebox.showerror("Erro", "A planilha deve conter pelo menos uma coluna 'EAN' ou 'SKU'.")
            return

        if "EAN" in columns and "SKU" in columns:
            confirm = messagebox.askyesno("Confirmação", "A planilha contém colunas 'EAN' e 'SKU'. Deseja gerar etiquetas com ambos os dados?")
            if not confirm:
                return

        label_format = messagebox.askquestion("Formato da Etiqueta", "Deseja gerar etiquetas em \n (SIM) 1-Coluna \n ou \n (NÃO) 2-Colunas?", icon='question')
        if label_format == 'yes':
            self.label_format.set("1-Coluna")
        else:
            self.label_format.set("2-Colunas")

        for _, row in data.iterrows():
            ean = int(row.get("EAN", ""))
            sku = str(row.get("SKU", "")).strip()
            quantity = int(row.get("Quantidade", ""))

            if not quantity:
                messagebox.showerror("Erro", "Quantidade inválida.")
                continue

            if self.code_type.get() == "EAN" and not ean:
                messagebox.showerror("Erro", "Por favor, preencha o campo EAN.")
                continue
            if self.code_type.get() == "SKU" and not sku:
                messagebox.showerror("Erro", "Por favor, preencha o campo SKU.")
                continue

            if self.code_type.get() == "EAN" and not EANValidator.is_valid_ean(ean):
                messagebox.showerror("Erro", "EAN inválido. Deve conter 8, 12, 13 ou 14 dígitos.")
                continue

            if any(ean == existing[0] and sku == existing[1] for existing in self.generator.eans_and_skus):
                messagebox.showwarning("Aviso", f"EAN {ean} e SKU {sku} já existem e foram desconsiderados.")
                continue

            self.generator.add_ean_sku(ean, sku, int(quantity))
            self.tree.insert("", tk.END, values=(ean, sku, quantity))

        messagebox.showinfo("Sucesso", "Dados processados e etiquetas geradas com sucesso!")