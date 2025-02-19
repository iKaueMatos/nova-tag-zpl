import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

class SheetImporter:
    def __init__(self, generator, tree, code_type):
        self.generator = generator
        self.tree = tree
        self.code_type = code_type

    def import_sheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("Planilhas", "*.csv *.xlsx")])
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
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            return pd.read_excel(file_path)

    def _clean_and_validate_data(self, data):
        """
        Trata e valida os dados usando Pandas.
        - Converte EAN e Quantidade para números.
        - Garante que SKU seja tratado como string.
        - Remove linhas com dados inválidos.
        """
        data["EAN"] = data["EAN"].astype(str).str.replace(".0", "", regex=False)
        data["SKU"] = data["SKU"].astype(str).str.replace(".0", "", regex=False)

        data["EAN"] = pd.to_numeric(data["EAN"], errors="coerce")

        data["Quantidade"] = pd.to_numeric(data["Quantidade"], errors="coerce")

        data = data.dropna(subset=["EAN", "Quantidade"])

        data = data[data["EAN"] != 0]

        data = data[data["Quantidade"] != 0]

        data = data[data["SKU"].str.match(r"^[a-zA-Z0-9]+$")]

        return data

    def _process_data(self, data):
        """
        Processa os dados tratados e os adiciona ao Treeview e ao gerador.
        """
        for _, row in data.iterrows():
            ean = int(row["EAN"])
            sku = str(row["SKU"])
            quantity = int(row["Quantidade"])

            self.generator.add_ean_sku(ean, sku, quantity)
            self.tree.insert("", tk.END, values=(ean, sku, quantity))

    def _parse_quantity(self, quantity_str):
        try:
            return int(float(quantity_str))
        except ValueError:
            raise ValueError(f"Quantidade inválida: '{quantity_str}'. Deve ser um número.")