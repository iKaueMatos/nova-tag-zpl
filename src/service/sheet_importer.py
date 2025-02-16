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
            self._process_data(data)
            messagebox.showinfo("Sucesso", "Dados importados com sucesso!")
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

    def _process_data(self, data):
        for row in data.itertuples(index=False):
            ean_str = str(getattr(row, "EAN", 0)).strip()
            sku_str = str(getattr(row, "SKU", "")).strip()
            quantity_str = str(getattr(row, "Quantidade", 0)).strip()

            if ean_str.endswith(".0"):
                ean_str = ean_str[:-2]

            quantity = self._parse_quantity(quantity_str)

            if self.code_type.get() == "EAN" and not ean_str:
                continue
            if self.code_type.get() == "SKU" and not sku_str:
                continue

            self.generator.add_ean_sku(ean_str, sku_str, quantity)
            self.tree.insert("", tk.END, values=(ean_str, sku_str, quantity))

    def _parse_quantity(self, quantity_str):
        try:
            return int(quantity_str)
        except ValueError:
            raise ValueError(f"Quantidade inválida: {quantity_str}")