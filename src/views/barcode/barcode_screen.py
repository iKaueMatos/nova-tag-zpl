from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import tkinter as tk
from tkinter import ttk
import math
from PIL import Image, ImageTk
import yaml

from src.core.config.config import Config
from src.core.config.enum.label_format_constants import LabelFormatConstants
from src.models.barcode_label_generator import BarcodeLabelGenerator
from src.service.sheet.download_template_service import TemplateDownloadService
from src.service.sheet.sheet_importer_service import SheetImporterService
from src.service.zebra.zebra_labelary_api_service import ZebraLabelaryApiService
from src.service.zebra.zebra_printer_service import ZebraPrinterService
from src.utils.dialog_center import DialogCenter
from src.views.manual.manualScreen.zpl_manual_screen import ZPLManualView
from src.service.validation.ean_validator import EANValidator

class BarcodeScreen:
    def __init__(self, root):
        self.root = root
        self.config = Config()
        self.generator = BarcodeLabelGenerator()
        self.printer_service = ZebraPrinterService()
        self.zpl_code = None
        self.selected_printer = self.config.load_saved_printer()
        self.zebra_labelary_api_service = ZebraLabelaryApiService()
        self.manual_eans = []
        self.manual_skus = []
        self.routes = self.load_routes()
        self.select_all_var = tk.BooleanVar()  # Variável para o checkbox de selecionar todos

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        self.build_menu_bar()
        self.build_left_panel()
        self.build_right_panel()
        self.bind_shortcuts()

        self.toggle_fields()

    def load_routes(self):
        with open('routes.yaml', 'r') as file:
            return yaml.safe_load(file)

    def build_menu_bar(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Configurações", menu=self.config_menu)

        self.config_menu.add_command(label="Selecionar Impressora", command=self.select_printer, accelerator="Ctrl+P")
        self.advanced_config_menu = tk.Menu(self.config_menu, tearoff=0)
        self.config_menu.add_cascade(label="Configurações Avançadas", menu=self.advanced_config_menu)
        self.advanced_config_menu.add_command(label="Ajustar Densidade", command=self.adjust_density)
        self.config_menu.add_command(label="Limpar Fila de Impressão", command=self.clear_print_queue)
        self.config_menu.add_command(label="Salvar Impressão", command=self.save_print_job)
        self.config_menu.add_command(label="Pausar Impressão", command=self.pause_print_job)

        self.actions_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ações", menu=self.actions_menu)
        self.actions_menu.add_command(label="Importar Planilha", command=self.import_sheet)
        self.actions_menu.add_command(label="Baixar Template", command=self.download_template)

        self.new_screens_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ferramentas Adicionais", menu=self.new_screens_menu)
        for screen_name in self.routes['screens']:
            self.new_screens_menu.add_command(label=screen_name, command=lambda name=screen_name: self.open_screen(name))

    def build_left_panel(self):
        self.left_frame = ttk.Frame(self.root, padding=20)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # Tipo de Código
        ttk.Label(self.left_frame, text="Tipo de Código:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.code_type = tk.StringVar(value="EAN")
        self.code_type_combobox = ttk.Combobox(self.left_frame, textvariable=self.code_type, state="readonly")
        self.code_type_combobox['values'] = ("EAN", "SKU", "Ambos")
        self.code_type_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.code_type_combobox.bind("<<ComboboxSelected>>", self.toggle_fields)

        # Formato da Etiqueta
        ttk.Label(self.left_frame, text="Formato da Etiqueta:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.label_format = tk.StringVar(value="1-Coluna")
        self.format_combobox = ttk.Combobox(self.left_frame, textvariable=self.label_format, state="readonly")
        self.format_combobox['values'] = ("1-Coluna", "2-Colunas")
        self.format_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # EAN / SKU / Quantidade
        ttk.Label(self.left_frame, text="EAN:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ean_entry = ttk.Entry(self.left_frame)
        self.ean_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.left_frame, text="SKU:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.sku_entry = ttk.Entry(self.left_frame)
        self.sku_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.left_frame, text="Quantidade:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.left_frame, width=10)
        self.quantity_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        self.add_button = ttk.Button(self.left_frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=4, column=2, sticky="e", padx=5, pady=5)

        tree_frame = ttk.Frame(self.left_frame)
        tree_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.tree = ttk.Treeview(tree_frame, columns=("EAN", "SKU", "Quantidade"), show="headings", height=14)
        self.tree.heading("EAN", text="EAN", command=lambda: self.sort_column("EAN", False))
        self.tree.heading("SKU", text="SKU", command=lambda: self.sort_column("SKU", False))
        self.tree.heading("Quantidade", text="Quantidade", command=lambda: self.sort_column("Quantidade", False))

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(expand=True, fill="both")
        self.left_frame.rowconfigure(5, weight=1)

        ttk.Label(self.left_frame, text="Código ZPL Gerado:").grid(row=6, column=0, columnspan=3, sticky="w", padx=5,
                                                                   pady=5)
        self.label_text = scrolledtext.ScrolledText(self.left_frame, width=50, height=10, state=tk.DISABLED)
        self.label_text.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.left_frame.rowconfigure(7, weight=1)

        self.select_all_checkbox = ttk.Checkbutton(self.left_frame, text="Selecionar Todos", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.grid(row=8, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        button_frame1 = ttk.Frame(self.left_frame)
        button_frame1.grid(row=9, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.generate_button = ttk.Button(button_frame1, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.pack(side="left", expand=True, fill="both")
        self.clear_button = ttk.Button(button_frame1, text="Limpar Dados", command=self.clear_data)
        self.clear_button.pack(side="left", expand=True, fill="both")

        button_frame2 = ttk.Frame(self.left_frame)
        button_frame2.grid(row=10, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.print_button = ttk.Button(button_frame2, text="Imprimir", command=self.print_label, state=tk.DISABLED)
        self.print_button.pack(side="left", expand=True, fill="both")
        self.save_button = ttk.Button(button_frame2, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.pack(side="left", expand=True, fill="both")
        self.root.bind("<Control-c>", self.copy_column)

        self.importer = SheetImporterService(self.generator, self.tree, self.code_type)
        self.template_download_service = TemplateDownloadService(self.root)

    def sort_column(self, col, reverse):
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def build_right_panel(self):
        self.right_frame = ttk.Frame(self.root, padding=20)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.preview_label = ttk.Label(self.right_frame, text="Imagem da Etiqueta")
        self.preview_label.grid(row=0, column=0, pady=10)

        preview_frame = ttk.LabelFrame(self.right_frame, text="Pré-visualização da Etiqueta")
        preview_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.preview_image_label = ttk.Label(preview_frame)
        self.preview_image_label.pack(expand=True, fill="both", padx=5, pady=5)

    def bind_shortcuts(self):
        self.root.bind("<Control-p>", self.select_printer)
        self.root.bind("<Control-a>", self.select_all_rows)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.root.bind("<Return>", lambda event: self.generate_zpl())
        self.tree.bind("<Double-1>", self.on_double_click)

    def clear_print_queue(self):
        """Limpa a fila de impressão utilizando o serviço de impressora Zebra."""
        self.printer_service.clear_print_queue()

    def update_preview(self):
        """
            Gera a imagem a partir do ZPL (via Labelary) e exibe no Label de preview.
        """
        if not self.zpl_code:
            return

        selected_label_format = self.label_format.get()
        if selected_label_format is None:
            messagebox.showerror("Erro", "Selecione um formato de etiqueta.")
            return

        def get_first_zpl_block(zpl_code):
            if "^XZ" in zpl_code:
                first_block = zpl_code.split("^XZ")[0] + "^XZ"
                return first_block
            return None

        zpl_code_to_send = get_first_zpl_block(self.zpl_code)

        if not zpl_code_to_send:
            messagebox.showerror("Erro", "Código ZPL inválido ou não encontrado.")
            return

        if selected_label_format == "2-Colunas":
            printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
            label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
            label_index = LabelFormatConstants.LABEL_INDEX_0
            output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        if selected_label_format == "1-Coluna":
            printer_density = LabelFormatConstants.PRINTER_DENSITY_8DPMM
            label_dimensions = LabelFormatConstants.LABEL_DIMENSIONS_5X25
            label_index = LabelFormatConstants.LABEL_INDEX_0
            output_format = LabelFormatConstants.OUTPUT_FORMAT_IMAGE

        image = self.zebra_labelary_api_service.generate_preview_image(
            zpl_code_to_send,
            printer_density,
            label_dimensions,
            label_index,
            output_format
        )

        if image:
            width, height = image.size
            new_width = 600
            new_height = int((new_width / width) * height)
            image = image.resize((new_width, new_height), Image.LANCZOS)

            self.preview_image_tk = ImageTk.PhotoImage(image)
            self.preview_image_label.config(image=self.preview_image_tk)
            self.preview_image_label.image = self.preview_image_tk
        else:
            messagebox.showerror("Erro", "Falha ao gerar a pré-visualização da etiqueta.")

    def minimize_main_window(self):
        self.root.iconify()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_preview)

    def on_close_preview(self):
        self.root.deiconify()
        self.root.destroy()

    def adjust_density(self):
        """Permite ao usuário ajustar a densidade de impressão através de uma caixa de entrada."""
        density_value = simpledialog.askinteger("Ajustar Densidade", "Escolha a densidade de 0 a 30:",
                                                minvalue=0, maxvalue=30, initialvalue=self.printer_service.density)
        if density_value is not None:
            self.printer_service.set_density(density_value)
            print(f"Densidade ajustada para: {density_value}")

    def select_printer(self):
        printers = self.printer_service.get_printers()
        if not printers:
            messagebox.showerror("Erro", "Nenhuma impressora disponível.")
            return

        def confirm_selection():
            selected = printer_var.get()
            if selected in printers:
                self.selected_printer = selected
                self.printer_service.set_printer(selected)
                self.config.save_printer(selected)
                messagebox.showinfo("Sucesso", f"Impressora selecionada: {selected}")
                popup.destroy()
            else:
                messagebox.showwarning("Aviso", "Selecione uma impressora válida.")

        popup = tk.Toplevel(self.root)
        popup.title("Selecionar Impressora")
        popup.geometry("400x200")
        popup.grab_set()

        DialogCenter.center_window(popup)

        tk.Label(popup, text="Escolha uma impressora:").pack(pady=5)

        printer_var = tk.StringVar(value=printers[0])

        printer_combobox = ttk.Combobox(popup, textvariable=printer_var, values=printers, state="readonly")
        printer_combobox.pack(pady=10, padx=10, fill="x")
        printer_combobox.config(width=30)
        printer_combobox.current(0)

        ttk.Button(popup, text="Confirmar", command=confirm_selection).pack(pady=10)

    def print_label(self):
        if not self.selected_printer:
            messagebox.showerror("Erro", "Selecione uma impressora antes de imprimir.")
            return

        zpl_data = self.label_text.get("1.0", tk.END).strip()
        if not zpl_data:
            messagebox.showerror("Erro", "Nenhum código ZPL para imprimir.")
            return

        confirm = messagebox.askyesno("Confirmação", "Deseja realmente imprimir a etiqueta?")
        if not confirm:
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

        self.label_text.config(state=tk.NORMAL)
        self.label_text.delete("1.0", tk.END)
        self.label_text.config(state=tk.DISABLED)

        self.zpl_code = None
        self.print_button.config(state=tk.DISABLED)
        self.select_printer_button.config(state=tk.DISABLED)
        messagebox.showinfo("Sucesso", "Todos os dados foram limpos.")

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

        if self.code_type.get() == "EAN" and not EANValidator.is_valid_ean(ean):
            messagebox.showerror("Erro", "EAN inválido. Deve conter 8, 12, 13 ou 14 dígitos.")
            return

        eans_exits = {item[0] for item in self.generator.eans_and_skus}
        skus_exist = {item[1] for item in self.generator.eans_and_skus}

        if ean in eans_exits or sku in skus_exist or ean in self.manual_eans or sku in self.manual_skus:
            messagebox.showwarning("Aviso", f"O EAN '{ean}' ou SKU '{sku}' já existem e foram desconsiderados.")
            for item in self.tree.get_children():
                item_values = self.tree.item(item, 'values')
                if item_values[0] == ean or item_values[1] == sku:
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
            return

        if self.code_type.get() == "EAN":
            self.generator.add_ean_sku(int(ean), "", int(quantity))
        if self.code_type.get() == "SKU":
            self.generator.add_ean_sku("", sku, int(quantity))
        if self.code_type.get() == "Ambos":
            self.generator.add_ean_sku(int(ean), sku, int(quantity))

        self.tree.insert("", tk.END, values=(ean, sku, quantity))
        self.manual_eans.append(ean)
        self.manual_skus.append(sku)

        self.ean_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def calculate_quantity_to_send(self, total_quantity, columns):
        if columns == 2:
            return total_quantity if total_quantity % 2 == 0 else total_quantity + 1
        elif columns == 4:
            return math.ceil(total_quantity / 4) * 4
        return total_quantity

    def import_sheet(self):
        self.importer.import_sheet()

    def download_template(self):
        self.template_download_service.download_template()

    def generate_zpl(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione ao menos uma linha na tabela.")
            return

        selected_type = self.code_type.get()
        labels_data = []

        for item in selected_items:
            item_values = self.tree.item(item, 'values')

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
        self.zpl_code = self.generator.generate_zpl()

        if self.zpl_code:
            self.label_text.config(state="normal")
            self.label_text.delete("1.0", tk.END)
            self.label_text.insert("1.0", self.zpl_code)
            self.label_text.config(state="disabled")
            self.print_button.config(state=tk.NORMAL)
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

    def on_row_click(self, event):
        """
            Captura as informações da linha selecionada.
        """
        selected_item = self.tree.selection()
        if selected_item:
            self.update_preview()

    def select_all_rows(self, event=None):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def open_zpl_manual(self):
        ZPLManualView(self.root, self.printer_service, self.zebra_labelary_api_service)

    def copy_column(self, event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item_values = self.tree.item(selected_item[0], "values")
        column_index = self.tree.identify_column(event.x)

        if column_index == "#1":
            value = item_values[0]
        elif column_index == "#2":
            value = item_values[1]
        elif column_index == "#3":
            value = item_values[2]
        else:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.root.update()
        messagebox.showinfo("Copiado!", f"Valor '{value}' copiado para a área de transferência.")

    def save_print_job(self):
        """Salva o código ZPL para impressão posterior"""
        zpl_data = self.label_text.get("1.0", tk.END).strip()
        if not zpl_data:
            messagebox.showerror("Erro", "Nenhum código ZPL para salvar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".zpl",
                                                 filetypes=[("Arquivos ZPL", "*.zpl"), ("Todos os arquivos", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(zpl_data)
            messagebox.showinfo("Sucesso", "Código ZPL salvo com sucesso!")

    def pause_print_job(self):
        """Pausa a impressão cancelando a fila da impressora"""
        confirm = messagebox.askyesno("Pausar Impressão", "Deseja realmente pausar a impressão?")
        if confirm:
            self.printer_service.clear_print_queue()
            messagebox.showinfo("Pausado", "A impressão foi pausada com sucesso.")

    def on_double_click(self, event):
        """Permite edição da coluna 'Quantidade' ao dar um duplo clique."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = selected_item[0]
        column_id = self.tree.identify_column(event.x)
        column_index = int(column_id[1:]) - 1

        if column_index != 2:
            return

        x, y, width, height = self.tree.bbox(item, column_index)
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)

        def save_edit(event):
            """Salva o novo valor e remove o campo de entrada."""
            new_value = entry.get().strip()
            if new_value.isdigit():
                self.tree.set(item, column="Quantidade", value=new_value)
            entry.destroy()

        entry.insert(0, self.tree.item(item, "values")[2])
        entry.focus()
        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())
        self.tree.bind("<Double-1>", self.on_double_click)

    def open_screen(self, screen_name):
        if screen_name == "Impressão ZPL":
            ZPLManualView(self.root, self.printer_service, self.zebra_labelary_api_service)
        else:
            messagebox.showinfo("Info", f"Tela '{screen_name}' não implementada.")

    def toggle_select_all(self):
        if self.select_all_var.get():
            self.select_all_rows()
        else:
            self.tree.selection_remove(self.tree.get_children())