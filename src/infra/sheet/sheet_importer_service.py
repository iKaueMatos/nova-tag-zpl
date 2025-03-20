# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
import tkinter as tk
from tkinter import messagebox, filedialog

import pandas as pd

from src.models import BarcodeLabelGenerator
from src.service.generator.strategy.add_both_strategy import AddBothStrategy
from src.service.generator.strategy.add_ean_strategy import AddEANStrategy
from src.service.generator.strategy.add_full_mercadolivre_strategy import AddFullMercadoLivreStrategy
from src.service.generator.strategy.add_sku_strategy import AddSKUStrategy
from src.service.validation.ean_validator import EANValidator
from src.utils.dialog_center import DialogCenter


class SheetImporterService:
    def __init__(self, generator, tree, code_type, label_format, label_text, print_button):
        self.generator = generator
        self.tree = tree
        self.code_type = code_type
        self.label_format = label_format
        self.label_text = label_text
        self.print_button = print_button

    def import_sheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("Planilhas", "*.csv *.xlsx *.xls *.ods")])
        if not file_path:
            return

        try:
            data = self._read_file(file_path)
            data = self._clean_and_validate_data(data)

            selected_code_type = self._ask_label_format()
            if not selected_code_type:
                messagebox.showwarning("Aviso", "Nenhum tipo de etiqueta selecionado.")
                return

            self.code_type.set(selected_code_type)

            self._process_data(data)

        except (pd.errors.EmptyDataError, ValueError) as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
        except pd.errors.ParserError:
            messagebox.showerror("Erro", "Erro ao ler o arquivo. Verifique o formato.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar planilha: {e}")

    def _read_file(self, file_path):
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
        required_columns = ["EAN", "SKU", "Código", "Descrição", "Tamanho", "Quantidade"]
        for col in required_columns:
            if col not in data.columns:
                data[col] = "-"

        data["EAN"] = data["EAN"].astype(str).fillna("-")
        data["SKU"] = data["SKU"].astype(str).fillna("-")
        data["Código"] = data["Código"].astype(str).fillna("-")
        data["Descrição"] = data["Descrição"].astype(str).fillna("-")
        data["Tamanho"] = data["Tamanho"].astype(str).fillna("-")
        data["Quantidade"] = pd.to_numeric(data["Quantidade"], errors="coerce").fillna(0).astype(int)

        data = data[(data["EAN"] != "-") | (data["SKU"] != "-")]

        data["EAN"] = pd.to_numeric(data["EAN"], errors="coerce")
        data = data.dropna(subset=["EAN", "Quantidade"])
        data = data[data["EAN"] != 0]
        data = data[data["Quantidade"] > 0]

        data = data[data["SKU"].str.match(r"^[a-zA-Z0-9\-]*$")]

        duplicated = data[data.duplicated(["EAN", "SKU", "Código"], keep=False)]
        if not duplicated.empty:
            messagebox.showwarning("Aviso", f"Algumas linhas foram desconsideradas por duplicação:\n{duplicated.to_string(index=False)}")
            data = data.drop_duplicates(["EAN", "SKU", "Código"], keep='first')

        return data

    def _ask_label_format(self):
        selected_code_type = None

        def on_submit():
            nonlocal selected_code_type

            if ean_var.get():
                selected_code_type = "EAN"
            elif sku_var.get():
                selected_code_type = "SKU"
            elif both_var.get():
                selected_code_type = "Ambos(EAN e SKU)"
            elif full_ml_var.get():
                selected_code_type = "Full Mercado Livre"

            if one_column_var.get():
                self.label_format.set("1-Coluna")
            elif two_column_var.get():
                self.label_format.set("2-Colunas")

            dialog.destroy()

        dialog = tk.Toplevel()
        dialog.geometry("600x400")
        dialog.title("Selecione o Tipo de Geração de Etiqueta")
        DialogCenter.center_window(dialog)

        ean_var = tk.BooleanVar()
        sku_var = tk.BooleanVar()
        both_var = tk.BooleanVar()
        full_ml_var = tk.BooleanVar()
        one_column_var = tk.BooleanVar()
        two_column_var = tk.BooleanVar()

        tk.Label(dialog, text="Selecione o tipo de código:").pack()
        tk.Checkbutton(dialog, text="EAN", variable=ean_var).pack()
        tk.Checkbutton(dialog, text="SKU", variable=sku_var).pack()
        tk.Checkbutton(dialog, text="Ambos (EAN e SKU)", variable=both_var).pack()
        tk.Checkbutton(dialog, text="Full Mercado Livre", variable=full_ml_var).pack()

        tk.Label(dialog, text="Selecione o formato da etiqueta:").pack()
        tk.Checkbutton(dialog, text="1-Coluna", variable=one_column_var).pack()
        tk.Checkbutton(dialog, text="2-Colunas", variable=two_column_var).pack()

        tk.Button(dialog, text="Confirmar", command=on_submit).pack()

        dialog.grab_set()
        dialog.wait_window()

        return selected_code_type

    def _process_data(self, data):
        strategy_map = {
            "EAN": AddEANStrategy(),
            "SKU": AddSKUStrategy(),
            "Ambos(EAN e SKU)": AddBothStrategy(),
            "Full Mercado Livre": AddFullMercadoLivreStrategy()
        }

        for _, row in data.iterrows():
            try:
                ean = int(row.get("EAN")) if pd.notnull(row.get("EAN")) else "-"
            except ValueError:
                ean = "-"

            sku = str(row.get("SKU", "-")).strip()
            quantity = int(row.get("Quantidade", 0))
            code = str(row.get("Código", "-")).strip()
            description = str(row.get("Descrição", "-")).strip()
            size = str(row.get("Tamanho", "-")).strip()

            if quantity <= 0:
                continue

            if self.code_type.get() == "EAN" and (ean == "-" or not EANValidator.is_valid_ean(str(ean))):
                continue

            if any(ean == existing[0] and sku == existing[1] for existing in self.generator.eans_and_skus):
                continue

            strategy = strategy_map.get(self.code_type.get())
            if strategy:
                strategy.add(self.generator, ean, sku, quantity, description, code, size)

            self.tree.insert("", tk.END, values=(ean, sku, quantity, description, code, size))

        messagebox.showinfo("Sucesso", "Dados processados")

        barcode_label_generator = BarcodeLabelGenerator()
        barcode_label_generator.eans_and_skus = self.generator.eans_and_skus
        barcode_label_generator.set_label_format(self.label_format.get())

        barcode_label_generator = BarcodeLabelGenerator()
        barcode_label_generator.eans_and_skus = self.generator.eans_and_skus
        barcode_label_generator.set_label_format(self.label_format.get())

        try:
            self.zpl_code = barcode_label_generator.generate_zpl()
            if self.zpl_code:
                self.label_text.config(state="normal")
                self.label_text.delete("1.0", tk.END)
                self.label_text.insert("1.0", self.zpl_code)
                self.label_text.config(state="disabled")
                self.print_button.config(state=tk.NORMAL)
                messagebox.showinfo("Sucesso", "Código ZPL gerado com sucesso!")
            else:
                messagebox.showerror("Erro", "Falha ao gerar o código ZPL.")
                self.print_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar ZPL: {e}")