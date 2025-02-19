import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import pandas as pd
import math
from src.models.barcode_label_generator import BarcodeLabelGenerator
from src.service.sheet_importer import SheetImporter
from src.service.zebra_printer_service import ZebraPrinterService


class BarcodeLabelApp:
    def __init__(self, root):
        self.generator = BarcodeLabelGenerator()
        self.printer_service = ZebraPrinterService()
        self.zpl_code = None
        self.selected_printer = None
        self.root = root

        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Configura expansão da janela
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)
        self.frame.columnconfigure(2, weight=1)

        # ----------------- Linha 0: Tipo de Código -----------------
        ttk.Label(self.frame, text="Tipo de Código:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.code_type = tk.StringVar(value="EAN")
        self.code_type_combobox = ttk.Combobox(self.frame, textvariable=self.code_type, state="readonly")
        self.code_type_combobox['values'] = ("EAN", "SKU", "Ambos")
        self.code_type_combobox.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.code_type_combobox['values'] = ("EAN", "SKU", "QRCode", "Code128", "Ambos")
        self.code_type_combobox.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.code_type_combobox.bind("<<ComboboxSelected>>", self.toggle_fields)

        # ----------------- Linha 1: EAN -----------------
        ttk.Label(self.frame, text="EAN:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ean_entry = ttk.Entry(self.frame)
        self.ean_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 2: SKU -----------------
        ttk.Label(self.frame, text="SKU:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.sku_entry = ttk.Entry(self.frame)
        self.sku_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 3: Quantidade e Botão Adicionar -----------------
        ttk.Label(self.frame, text="Quantidade:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.frame, width=10)
        self.quantity_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.add_button = ttk.Button(self.frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=3, column=2, sticky="e", padx=5, pady=5)

        # ----------------- Linha 4: TreeView -----------------
        self.tree = ttk.Treeview(self.frame, columns=("EAN", "SKU", "Quantidade"), show="headings", height=8)
        self.tree.heading("EAN", text="EAN")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.frame.rowconfigure(4, weight=1)

        # ----------------- Linha 5: Rótulo para o ZPL -----------------
        ttk.Label(self.frame, text="Código ZPL Gerado:").grid(row=5, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        # ----------------- Linha 6: Área de Texto (desabilitada) -----------------
        self.label_text = scrolledtext.ScrolledText(self.frame, width=50, height=10, state=tk.DISABLED)
        self.label_text.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.frame.rowconfigure(6, weight=1)

        # ----------------- Linha 7: Botões de Ação (linha 1) -----------------
        button_frame1 = ttk.Frame(self.frame)
        button_frame1.grid(row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        button_frame1.columnconfigure(0, weight=1)
        button_frame1.columnconfigure(1, weight=1)
        button_frame1.columnconfigure(2, weight=1)

        self.importer = SheetImporter(self.generator, self.tree, self.code_type)
        self.import_button = ttk.Button(button_frame1, text="Importar Planilha", command=self.import_sheet)
        self.import_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.generate_button = ttk.Button(button_frame1, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.clear_button = ttk.Button(button_frame1, text="Limpar Dados", command=self.clear_data)
        self.clear_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 8: Botões de Ação (linha 2) -----------------
        button_frame2 = ttk.Frame(self.frame)
        button_frame2.grid(row=8, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        button_frame2.columnconfigure(0, weight=1)
        button_frame2.columnconfigure(1, weight=1)
        button_frame2.columnconfigure(2, weight=1)
        self.select_printer_button = ttk.Button(button_frame2, text="Selecionar Impressora",
                                                command=self.select_printer, state=tk.DISABLED)
        self.select_printer_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.print_button = ttk.Button(button_frame2, text="Imprimir",
                                       command=self.print_label, state=tk.DISABLED)

        self.print_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.download_button = ttk.Button(button_frame2, text="Baixar Template", command=self.download_template)
        self.download_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        self.save_button = ttk.Button(button_frame2, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        # ----------------- Linha 9: Formato da Etiqueta -----------------
        ttk.Label(self.frame, text="Formato da Etiqueta:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.label_format = tk.StringVar(value="2-Colunas")
        self.format_combobox = ttk.Combobox(self.frame, textvariable=self.label_format, state="readonly")
        self.format_combobox['values'] = ("2-Colunas", "1-Coluna")
        self.format_combobox.grid(row=9, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.format_combobox['values'] = ("1-Coluna", "2-Colunas")
        self.format_combobox.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.format_combobox.current(0)

        self.root.bind('<Return>', lambda event: self.generate_zpl())
        self.toggle_fields()

    def select_printer(self):
        printers = self.printer_service.get_printers()
        if not printers:
            messagebox.showerror("Erro", "Nenhuma impressora disponível.")
            return

        printer_name = simpledialog.askstring("Selecionar Impressora", "Escolha uma impressora:",
                                              initialvalue=printers[0])
        if printer_name and printer_name in printers:
            self.selected_printer = printer_name
            self.printer_service.set_printer(printer_name)
            messagebox.showinfo("Sucesso", f"Impressora selecionada: {printer_name}")
        else:
            messagebox.showwarning("Aviso", "Nenhuma impressora selecionada.")

    def print_label(self):
        if not self.selected_printer:
            messagebox.showerror("Erro", "Selecione uma impressora antes de imprimir.")
            return

        zpl_data = self.label_text.get("1.0", tk.END).strip()
        if not zpl_data:
            messagebox.showerror("Erro", "Nenhum código ZPL para imprimir.")
            return

        self.printer_service.print_label(zpl_data)
        messagebox.showinfo("Sucesso", "Etiqueta enviada para a impressora.")

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
        elif self.code_type.get() == "Code128":
            self.ean_entry.config(state="disabled")
            self.sku_entry.config(state="normal")
        elif self.code_type.get() == "EAN":
            self.ean_entry.config(state="disabled")
            self.sku_entry.config(state="normal")
        elif self.code_type.get() == "QRCode":
            self.ean_entry.config(state="disabled")
            self.sku_entry.config(state="normal")

    def clear_data(self):
        if self.tree.get_children():
            self.tree.delete(*self.tree.get_children())
            self.generator.eans_and_skus.clear()
            messagebox.showinfo("Sucesso", "Todos os dados foram limpos.")
        else:
            messagebox.showinfo("Informação", "Nenhum dado para limpar.")

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

        item_id = self.tree.insert("", tk.END, values=(ean, sku, quantity, ""))
        self._add_action_buttons(item_id)

        self.ean_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def _add_action_buttons(self, item_id):
        action_frame = ttk.Frame(self.tree)
        action_frame.grid(row=0, column=0, sticky=tk.W)

        remove_button = ttk.Button(action_frame, text="Remover", command=lambda: self.remove_entry(item_id))
        remove_button.pack(side=tk.LEFT, padx=2)

        edit_button = ttk.Button(action_frame, text="Editar", command=lambda: self.edit_entry(item_id))
        edit_button.pack(side=tk.LEFT, padx=2)

        self.tree.set(item_id, "Ações", action_frame)

    def remove_entry(self, item_id):
        item_values = self.tree.item(item_id, "values")
        ean, sku, quantity, _ = item_values

        self.generator.eans_and_skus = [
            item for item in self.generator.eans_and_skus
            if item["ean"] != ean or item["sku"] != sku or item["quantity"] != int(quantity)
        ]

        self.tree.delete(item_id)
        messagebox.showinfo("Sucesso", "Item removido com sucesso.")

    def edit_entry(self, item_id):
        item_values = self.tree.item(item_id, "values")
        ean, sku, quantity, _ = item_values

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Item")

        ttk.Label(edit_window, text="EAN:").grid(row=0, column=0, padx=5, pady=5)
        ean_entry = ttk.Entry(edit_window, width=30)
        ean_entry.insert(0, ean)
        ean_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="SKU:").grid(row=1, column=0, padx=5, pady=5)
        sku_entry = ttk.Entry(edit_window, width=30)
        sku_entry.insert(0, sku)
        sku_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
        quantity_entry = ttk.Entry(edit_window, width=10)
        quantity_entry.insert(0, quantity)
        quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_changes():
            new_ean = ean_entry.get().strip()
            new_sku = sku_entry.get().strip()
            new_quantity = quantity_entry.get().strip()

            if not new_quantity.isdigit():
                messagebox.showerror("Erro", "Quantidade inválida.")
                return

            self.tree.item(item_id, values=(new_ean, new_sku, new_quantity, ""))

            self.generator.eans_and_skus = [
                item for item in self.generator.eans_and_skus
                if item["ean"] != ean or item["sku"] != sku or item["quantity"] != int(quantity)
            ]
            self.generator.add_ean_sku(int(new_ean), new_sku, int(new_quantity))

            messagebox.showinfo("Sucesso", "Item atualizado com sucesso.")
            edit_window.destroy()

        save_button = ttk.Button(edit_window, text="Salvar", command=save_changes)
        save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def calculate_quantity_to_send(self, total_quantity, columns):
        if columns == 2:
            return total_quantity if total_quantity % 2 == 0 else total_quantity + 1
        elif columns == 4:
            return math.ceil(total_quantity / 4) * 4
        return total_quantity

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
        labels_data = []

        for item in selected_items:
            item_values = self.tree.item(item, 'values')

            if len(item_values) < 3:
                messagebox.showerror("Erro", f"Dados inválidos na linha: {item_values}")
                continue

            ean, sku, quantity_str = item_values

            if not quantity_str.isdigit():
                messagebox.showwarning("Aviso", f"Quantidade inválida na linha: {item_values}. Ignorando.")
                continue

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

        self.generator.eans_and_skus.clear()

        for ean, sku, quantity in labels_data:
            if selected_type == "EAN":
                self.generator.add_ean_sku(ean, "", quantity)
            elif selected_type == "SKU":
                self.generator.add_ean_sku("", sku, quantity)
            else:
                self.generator.add_ean_sku(ean, sku, quantity)

        self.generator.set_label_format(label_format)
        self.zpl_code = self.generator.generate_zpl(label_format=label_format)

        if self.zpl_code:
            self.label_text.config(state="normal")
            self.label_text.delete("1.0", tk.END)
            self.label_text.insert("1.0", self.zpl_code)
            self.label_text.config(state="disabled")
            self.print_button.config(state=tk.NORMAL)
            self.select_printer_button.config(state=tk.NORMAL)
            messagebox.showinfo("Sucesso", "Código ZPL gerado com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao gerar o código ZPL.")

    def save_zpl(self):
        if not self.zpl_code:
            messagebox.showerror("Erro", "Nenhum código ZPL gerado. Gere antes de salvar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".zpl",
                                                 filetypes=[("Arquivo ZPL", "*.zpl")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.zpl_code)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em: {file_path}")