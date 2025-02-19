import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import math
from src.models.barcode_label_generator import BarcodeLabelGenerator
from src.service.sheet_importer import SheetImporter

class BarcodeLabelApp:
    def __init__(self, root):
        self.generator = BarcodeLabelGenerator()
        self.root = root

        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        for col in range(3):
            self.frame.columnconfigure(col, weight=1)

        ttk.Label(self.frame, text="Tipo de Código:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.code_type = tk.StringVar(value="EAN")
        self.code_type_combobox = ttk.Combobox(self.frame, textvariable=self.code_type, state="readonly")
        self.code_type_combobox['values'] = ("EAN", "SKU", "Ambos")
        self.code_type_combobox.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.code_type_combobox.bind("<<ComboboxSelected>>", self.toggle_fields)

        ttk.Label(self.frame, text="EAN:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.ean_entry = ttk.Entry(self.frame, width=30)
        self.ean_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.frame, text="SKU:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.sku_entry = ttk.Entry(self.frame, width=30)
        self.sku_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.frame, text="Quantidade:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.frame, width=10)
        self.quantity_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.add_button = ttk.Button(self.frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)

        self.tree = ttk.Treeview(self.frame, columns=("EAN", "SKU", "Quantidade"), show="headings", height=8)
        self.tree.heading("EAN", text="EAN")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.grid(row=4, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)

        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S), padx=(0, 5), pady=5)

        self.importer = SheetImporter(self.generator, self.tree, self.code_type)
        self.import_button = ttk.Button(self.frame, text="Importar Planilha", command=self.import_sheet)
        self.import_button.grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)

        self.generate_button = ttk.Button(self.frame, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        self.save_button = ttk.Button(self.frame, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.grid(row=5, column=2, sticky=tk.E, padx=5, pady=5)

        ttk.Label(self.frame, text="Formato da Etiqueta:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.label_format = tk.StringVar(value="2-Colunas")
        self.format_combobox = ttk.Combobox(self.frame, textvariable=self.label_format, state="readonly")
        self.format_combobox['values'] = ("2-Colunas", "1-Coluna", "QRCode", "Code128")
        self.format_combobox.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.format_combobox.current(0)

        self.download_button = ttk.Button(self.frame, text="Baixar Template", command=self.download_template)
        self.download_button.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=10)

        self.root.bind('<Return>', lambda event: self.generate_zpl())

        self.toggle_fields()

    def toggle_fields(self, event=None):
        if self.code_type.get() == "EAN":
            self.ean_entry.config(state="normal")
            self.sku_entry.config(state="disabled")
        elif self.code_type.get() == "SKU":
            self.sku_entry.config(state="normal")
            self.ean_entry.config(state="disabled")
        elif self.code_type.get() == "Ambos":
            self.ean_entry.config(state="normal")
            self.sku_entry.config(state="normal")

    def add_entry(self):
        ean = self.ean_entry.get().strip()
        sku = self.sku_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not quantity.isdigit():
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        if self.code_type.get() == "EAN" and not ean:
            messagebox.showerror("Erro", "Por favor, preencha o campo EAN.")
            return
        if self.code_type.get() == "SKU" and not sku:
            messagebox.showerror("Erro", "Por favor, preencha o campo SKU.")
            return

        if self.code_type.get() == "EAN":
            self.generator.add_ean_sku(int(ean), "", int(quantity))
        if self.code_type.get() == "SKU":
            self.generator.add_ean_sku("", sku, int(quantity))
        if self.code_type.get() == "Ambos":
            self.generator.add_ean_sku(int(ean), sku, int(quantity))

        self.tree.insert("", tk.END, values=(ean, sku, quantity))

        self.ean_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def download_template(self):
        def on_select_template_type():
            selected_type = self.template_type.get()
            template_data = pd.DataFrame()

            if selected_type == "EAN":
                template_data = pd.DataFrame({
                    "EAN": ["", "", ""],
                    "Quantidade": [0, 0, 0]
                })
            elif selected_type == "SKU":
                template_data = pd.DataFrame({
                    "SKU": ["", "", ""],
                    "Quantidade": [0, 0, 0]
                })
            elif selected_type == "Ambos":
                template_data = pd.DataFrame({
                    "EAN": ["", "", ""],
                    "SKU": ["", "", ""],
                    "Quantidade": [0, 0, 0]
                })

            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV", "*.csv")])
            if file_path:
                try:
                    template_data.to_csv(file_path, index=False)
                    messagebox.showinfo("Sucesso", f"Template salvo em: {file_path}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar o template: {e}")
            dialog.destroy()

        dialog = tk.Toplevel(self.root)
        dialog.title("Escolha o tipo de Planilha")

        ttk.Label(dialog, text="Selecione o tipo de planilha que deseja gerar:") \
            .grid(row=0, column=0, pady=10, padx=10)

        self.template_type = tk.StringVar(value="EAN")
        type_combobox = ttk.Combobox(dialog, textvariable=self.template_type, state="readonly")
        type_combobox['values'] = ("EAN", "SKU", "Ambos")
        type_combobox.grid(row=1, column=0, pady=10, padx=10)

        generate_button = ttk.Button(dialog, text="Gerar Template", command=on_select_template_type)
        generate_button.grid(row=2, column=0, pady=10, padx=10)

        dialog.grab_set()
        dialog.mainloop()

    def import_sheet(self):
        self.importer.import_sheet()

    def generate_zpl(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione ao menos uma linha na tabela.")
            return

        selected_type = self.code_type.get()

        if hasattr(self.generator, "eans_and_skus"):
            self.generator.eans_and_skus.clear()

        labels_data = []

        for item in selected_items:
            item_values = self.tree.item(item, 'values')
            ean, sku, quantity_str = item_values

            if not quantity_str.isdigit():
                messagebox.showerror("Erro", f"Quantidade inválida na linha: {item_values}")
                return

            quantity = int(quantity_str)

            if selected_type == "EAN" and not ean:
                continue
            if selected_type == "SKU" and not sku:
                continue

            label_format = self.label_format.get()
            columns = 1

            if label_format == "2-Colunas":
                columns = 2
            elif label_format == "4-etiquetas por página":
                columns = 4

            adjusted_quantity = self.calculate_quantity_to_send(quantity, columns)
            labels_data.append((ean, sku, adjusted_quantity))

        if not labels_data:
            messagebox.showerror("Erro", "Nenhum dado válido para gerar etiquetas.")
            return

        for ean, sku, quantity in labels_data:
            if selected_type == "EAN":
                self.generator.add_ean_sku(ean, "", quantity)
            elif selected_type == "SKU":
                self.generator.add_ean_sku("", sku, quantity)
            else:
                self.generator.add_ean_sku(ean, sku, quantity)

        self.generator.set_label_format(label_format)
        zpl_code = self.generator.generate_zpl(label_format=label_format)

        if zpl_code:
            messagebox.showinfo("Sucesso", "Código ZPL gerado com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao gerar o código ZPL.")

    def calculate_quantity_to_send(self, total_quantity, columns):
        if columns == 2:
            return total_quantity if total_quantity % 2 == 0 else total_quantity + 1
        elif columns == 4:
            return math.ceil(total_quantity / 4) * 4
        return total_quantity

    def save_zpl(self):
        if not self.generator.eans_and_skus:
            messagebox.showerror("Erro", "Nenhum dado para salvar etiqueta. Adicione EANs e SKUs primeiro.")
            return

        zpl_code = self.generator.generate_zpl(self.label_format.get())
        file_path = filedialog.asksaveasfilename(defaultextension=".zpl",
                                                 filetypes=[("Arquivo ZPL", "*.zpl")])
        if file_path:
            self.generator.save_zpl_to_file(zpl_code, file_path)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em: {file_path}")