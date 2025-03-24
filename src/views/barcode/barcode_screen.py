# ----------------------------------------------------------------------------
 # Autor: Kaue de Matos
 # Empresa: Nova Software
 # Propriedade da Empresa: Todos os direitos reservados
 # ----------------------------------------------------------------------------
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import tkinter as tk
from tkinter import ttk
import math

from src.core.config.config import Config
from src.core.config.enum.label_format_constants import LabelFormatConstants
from src.infra.printer.LabelPrinter import LabelPrinter
from src.infra.sheet.download_template_service import TemplateDownloadService
from src.infra.sheet.sheet_importer_service import SheetImporterService
from src.infra.zebra.zebra_labelary_api_service import ZebraLabelaryApiService
from src.infra.zebra.zebra_printer_service import ZebraPrinterService
from src.models import BarcodeLabelGenerator
from src.service.generator.strategy.add_both_strategy import AddBothStrategy
from src.service.generator.strategy.add_ean_strategy import AddEANStrategy
from src.service.generator.strategy.add_full_amazon_strategy import AddFullAmazonStrategy
from src.service.generator.strategy.add_full_mercadolivre_strategy import AddFullMercadoLivreStrategy
from src.service.generator.strategy.add_sku_strategy import AddSKUStrategy
from src.utils.dialog_center import DialogCenter
from src.service.validation.ean_validator import EANValidator
from src.views.printerzpl.zpl_manual_screen import ZPLManualView
from src.infra.repositories.printer_repo import PrinterRepository
from src.views.modal.show_shortcuts import ShowShortcuts

class BarcodeScreen:

    def __init__(self, root):
        self.root = root
        self.config = Config()
        self.generator = BarcodeLabelGenerator()
        self.printer_service = ZebraPrinterService()
        self.zpl_code = None
        self.selected_printer = self.config.load_saved_printer()
        self.zebra_labelary_api_service = ZebraLabelaryApiService()
        self.label_printer = LabelPrinter(self.root)
        self.manual_eans = []
        self.manual_skus = []
        self.manual_code_product = []

        self.select_all_var = tk.BooleanVar()
        self.selected_printer_id = None

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        self.build_menu_bar()
        self.build_left_panel()
        self.build_right_panel()
        self.bind_shortcuts()
        self.check_existing_printer()
        self.toggle_fields()
        self.create_context_menu()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Editar Etiqueta", command=self.edit_label_data)
        self.context_menu.add_command(label="Remover Item", command=self.remove_selected)

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

        # Tela dinamica | Routes.yaml
        self.new_screens_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ferramentas Adicionais", menu=self.new_screens_menu)
        self.new_screens_menu.add_command(label="Impressao ZPL", command=lambda name="Impressao ZPL": self.open_screen("Impressao ZPL"))

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ajuda", menu=self.help_menu)
        self.help_menu.add_command(label="Atalhos", command=lambda: ShowShortcuts.show_shortcuts(self.root))

    def build_left_panel(self):
        self.left_frame = ttk.Frame(self.root, padding=10)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.left_frame, text="Tipo de Código:").grid(row=0, column=0, sticky="w", padx=1, pady=1)
        self.code_type = tk.StringVar(value="EAN")
        self.code_type_combobox = ttk.Combobox(self.left_frame, textvariable=self.code_type, state="readonly", width=15)
        self.code_type_combobox['values'] = ("EAN", "SKU", "Ambos(EAN e SKU)", "Full Mercado Livre", "Full Amazon")
        self.code_type_combobox.grid(row=0, column=1, sticky="ew", padx=2, pady=1)
        self.code_type_combobox.bind("<<ComboboxSelected>>", self.toggle_fields)

        ttk.Label(self.left_frame, text="Formato da Etiqueta:").grid(row=1, column=0, sticky="w", padx=1, pady=1)
        self.label_format = tk.StringVar(value="1-Coluna")
        self.format_combobox = ttk.Combobox(self.left_frame, textvariable=self.label_format, state="readonly", width=15)
        self.format_combobox['values'] = ("1-Coluna", "2-Colunas")
        self.format_combobox.grid(row=1, column=1, sticky="ew", padx=2, pady=1)

        entry_frame = ttk.Frame(self.left_frame)
        entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Label(entry_frame, text="EAN:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ean_entry = ttk.Entry(entry_frame, width=30)
        self.ean_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(entry_frame, text="SKU:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.sku_entry = ttk.Entry(entry_frame, width=30)
        self.sku_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(entry_frame, text="Descrição:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.description_entry = ttk.Entry(entry_frame, width=30)
        self.description_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(entry_frame, text="Código:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.code_product_entry = ttk.Entry(entry_frame, width=30)
        self.code_product_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(entry_frame, text="Tamanho:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.size_entry = ttk.Entry(entry_frame, width=30)
        self.size_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(entry_frame, text="Quantidade:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.quantity_entry = ttk.Entry(entry_frame, width=30)
        self.quantity_entry.grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        self.add_button = ttk.Button(self.left_frame, text="Adicionar", command=self.add_entry)
        self.add_button.grid(row=3, column=1, sticky="e", padx=4, pady=4)

        tree_frame = ttk.Frame(self.left_frame)
        tree_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("EAN", "SKU", "Quantidade", "Descrição", "Código", "Tamanho"),
            show="headings",
            height=14
        )

        self.tree.heading("EAN", text="EAN", command=lambda: self.sort_column("EAN", False))
        self.tree.heading("SKU", text="SKU", command=lambda: self.sort_column("SKU", False))
        self.tree.heading("Quantidade", text="Quantidade", command=lambda: self.sort_column("Quantidade", False))
        self.tree.heading("Descrição", text="Descrição", command=lambda: self.sort_column("Descrição", False))
        self.tree.heading("Código", text="Código", command=lambda: self.sort_column("Código", False))
        self.tree.heading("Tamanho", text="Tamanho", command=lambda: self.sort_column("Tamanho", False))

        self.tree.column("EAN", anchor="center", width=120)
        self.tree.column("SKU", anchor="center", width=120)
        self.tree.column("Quantidade", anchor="center", width=100)
        self.tree.column("Descrição", anchor="w", width=200)
        self.tree.column("Código", anchor="center", width=120)
        self.tree.column("Tamanho", anchor="center", width=80)

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(expand=True, fill="both")

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.left_frame.rowconfigure(4, weight=1)

        ttk.Label(self.left_frame, text="Código ZPL Gerado:").grid(row=5, column=0, columnspan=3, sticky="w", padx=5,
                                                                   pady=5)
        self.label_text = scrolledtext.ScrolledText(self.left_frame, width=50, height=10, state=tk.DISABLED)
        self.label_text.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.left_frame.rowconfigure(6, weight=1)

        self.select_all_checkbox = ttk.Checkbutton(self.left_frame, text="Selecionar Todos \n informações da tabela",
                                                   variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.grid(row=7, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        button_frame = ttk.Frame(self.left_frame)
        button_frame.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

        self.generate_button = ttk.Button(button_frame, text="Gerar ZPL", command=self.generate_zpl)
        self.generate_button.pack(side="left", expand=True, fill="both", padx=3)

        self.clear_button = ttk.Button(button_frame, text="Limpar Dados", command=self.clear_data)
        self.clear_button.pack(side="left", expand=True, fill="both", padx=3)

        self.print_button_zpl = ttk.Button(button_frame, text="Imprimir Etiqueta(ZPL)", command=self.print_label, state=tk.DISABLED)
        self.print_button_zpl.pack(side="left", expand=True, fill="both", padx=3)

        self.print_button_pdf = ttk.Button(button_frame, text="Imprimir Etiqueta(PDF)", command=self.print_pdf_label, state=tk.DISABLED)
        self.print_button_pdf.pack(side="left", expand=True, fill="both", padx=3)

        self.save_button = ttk.Button(button_frame, text="Salvar ZPL", command=self.save_zpl)
        self.save_button.pack(side="left", expand=True, fill="both", padx=3)

        self.root.bind("<Control-c>", self.copy_column)

        self.importer = SheetImporterService(self.generator, self.tree, self.code_type, self.label_format, self.label_text, self.print_button_zpl)
        self.template_download_service = TemplateDownloadService(self.root)

    def toggle_fields(self, event=None):
        disabled_bg = "#d9d9d9"
        normal_bg = "white"

        if self.code_type.get() == "EAN":
            self.ean_entry.config(state="normal", background=normal_bg)
            self.sku_entry.config(state="disabled", background=disabled_bg)
            self.description_entry.config(state="disabled", background=disabled_bg)
            self.code_product_entry.config(state="disabled", background=disabled_bg)
            self.size_entry.config(state="disabled", background=disabled_bg)

            self.set_tooltip(self.sku_entry, "Campo desativado para EAN")
            self.set_tooltip(self.description_entry, "Campo desativado para EAN")
            self.set_tooltip(self.size_entry, "Campo desativado para EAN")
            self.set_tooltip(self.code_product_entry, "Campo desativado para EAN")

        if self.code_type.get() == "SKU":
            self.sku_entry.config(state="normal", background=normal_bg)
            self.ean_entry.config(state="disabled", background=disabled_bg)
            self.description_entry.config(state="disabled", background=disabled_bg)
            self.code_product_entry.config(state="disabled", background=disabled_bg)
            self.size_entry.config(state="disabled", background=disabled_bg)

            self.set_tooltip(self.ean_entry, "Campo desativado para SKU")
            self.set_tooltip(self.description_entry, "Campo desativado para SKU")
            self.set_tooltip(self.code_product_entry, "Campo desativado para SKU")
            self.set_tooltip(self.size_entry, "Campo desativado para SKU")

        if self.code_type.get() == "Ambos(EAN e SKU)":
            self.ean_entry.config(state="normal", background=normal_bg)
            self.sku_entry.config(state="normal", background=normal_bg)
            self.description_entry.config(state="disabled", background=disabled_bg)
            self.code_product_entry.config(state="disabled", background=disabled_bg)
            self.size_entry.config(state="disabled", background=disabled_bg)

            self.set_tooltip(self.description_entry, "Campo desativado para Ambos")
            self.set_tooltip(self.size_entry, "Campo desativado para Ambos")
            self.set_tooltip(self.code_product_entry, "Campo desativado para Ambos")
            self.set_tooltip(self.description_entry, "Campo desativado para Ambos")

        if self.code_type.get() == "Full Mercado Livre":
            self.sku_entry.config(state="normal", background=normal_bg)
            self.description_entry.config(state="normal", background=normal_bg)
            self.code_product_entry.config(state="normal", background=normal_bg)
            self.size_entry.config(state="normal", background=normal_bg)
            self.ean_entry.config(state="disabled", background=disabled_bg)

            self.set_tooltip(self.ean_entry, "Campo desativado para Full Mercado Livre")
            self.set_tooltip(self.size_entry, "Tamanho do produto(ex: P,M,G,GG)")
            self.set_tooltip(self.code_product_entry, "Código da etiqueta do mercado livre")
            self.set_tooltip(self.description_entry, "Mini descrição do produto")
            self.set_tooltip(self.sku_entry, "Sku da variação do produto")

        if self.code_type.get() == "Full Amazon":
            self.sku_entry.config(state="normal", background=normal_bg)
            self.description_entry.config(state="normal", background=normal_bg)
            self.code_product_entry.config(state="normal", background=normal_bg)
            self.size_entry.config(state="disabled", background=disabled_bg)
            self.ean_entry.config(state="disabled", background=disabled_bg)

            self.set_tooltip(self.ean_entry, "Campo desativado para Full Amazon")
            self.set_tooltip(self.size_entry, "Campo desativado para Full Amazon")
            self.set_tooltip(self.code_product_entry, "Código da etiqueta do Full amazon")
            self.set_tooltip(self.description_entry, "Mini descrição do produto")
            self.set_tooltip(self.sku_entry, "Sku da variação do produto")

    def set_tooltip(self, widget, text):
        def on_enter(event):
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.overrideredirect(True)
            self.tooltip.geometry(f"+{widget.winfo_rootx() + 20}+{widget.winfo_rooty() + 20}")
            label = tk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1, padx=5,
                             pady=2)
            label.pack()

        def on_leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

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

        self.pdf_button = ttk.Button(self.right_frame, text="Gerar PDF", compound=tk.LEFT, command=self.generate_pdf, state=tk.DISABLED)
        self.pdf_button.grid(row=2, column=0, pady=10)

    def bind_shortcuts(self):
        self.root.bind("<Control-p>", self.select_printer)
        self.root.bind("<Control-a>", self.select_all_rows)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.root.bind("<Return>", lambda event: self.generate_zpl())
        self.tree.bind("<Double-1>", self.on_double_click)
        self.label_text.bind("<Button-1>", self.copy_zpl)
        self.root.bind("<Button-1>", self.deselect_on_click_outside)

    def clear_print_queue(self):
        """Limpa a fila de impressão utilizando o serviço de impressora Zebra."""
        self.printer_service.clear_print_queue()

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

    def check_existing_printer(self):
        printers = PrinterRepository.list_all_printers()
        if printers:
            self.selected_printer = printers[0]['option_printer']
            self.print_button_zpl.config(state=tk.NORMAL)
        else:
            self.print_button_zpl.config(state=tk.DISABLED)

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
                PrinterRepository.insert_printer(selected)
                messagebox.showinfo("Sucesso", f"Impressora selecionada: {selected}")
                self.print_button_zpl.config(state=tk.NORMAL)
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

    def print_pdf_label(self, pdf_file_path):
        """Imprime o PDF gerado usando o caminho do arquivo PDF."""
        if not pdf_file_path:
            messagebox.showerror("Erro", "Nenhum arquivo PDF válido encontrado.")
            return

        confirm = messagebox.askyesno("Confirmação", "Deseja realmente imprimir o PDF?")
        if not confirm:
            return

        try:
            self.label_printer.print_pdf(pdf_file_path)
            messagebox.showinfo("Sucesso", "PDF enviado para a impressora.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar o PDF para a impressora: {str(e)}")

    def clear_data(self):
        if self.tree.get_children():
            self.tree.delete(*self.tree.get_children())
            self.generator.eans_and_skus.clear()

        self.label_text.config(state=tk.NORMAL)
        self.label_text.delete("1.0", tk.END)
        self.label_text.config(state=tk.DISABLED)

        self.zpl_code = None
        self.print_button_zpl.config(state=tk.DISABLED)
        self.print_button_pdf.config(state=tk.DISABLED)

        self.preview_image_label.config(image="")
        self.preview_image_label.image = None

        messagebox.showinfo("Sucesso", "Todos os dados foram limpos.")

    def add_entry(self):
        ean = self.ean_entry.get().strip()
        sku = self.sku_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        description = self.description_entry.get().strip()
        size = self.size_entry.get().strip()
        code = self.code_product_entry.get().strip()
        code_type = self.code_type.get()

        self.preview_image_label.config(image="")
        self.preview_image_label.image = None

        ean = ean if ean else "-"
        sku = sku if sku else "-"
        description = description if description else "-"
        size = size if size else "-"
        code = code if code else "-"

        if not quantity.isdigit():
            messagebox.showerror("Erro", "Quantidade inválida.")
            return
        quantity = int(quantity)

        if code_type == "Full Mercado Livre" and code != "-" and len(code) != 9:
            messagebox.showerror("Erro",
                                 "O código inserido deve ter exatamente 9 caracteres no modelo de etiqueta (Full Mercado Livre).")
            return

        if code_type == "Full Amazon" and code != "-" and len(code) != 10:
            messagebox.showerror("Erro",
                                 "O código inserido deve ter exatamente 10 caracteres no modelo de etiqueta (Full Amazon).")
            return

        if code_type == "EAN":
            if ean == "-":
                messagebox.showerror("Erro", "Por favor, preencha o campo EAN.")
                return
            if not EANValidator.is_valid_ean(ean):
                messagebox.showerror("Erro", "EAN inválido. Deve conter 8, 12, 13 ou 14 dígitos.")
                return
        elif code_type == "SKU" and sku == "-":
            messagebox.showerror("Erro", "Por favor, preencha o campo SKU.")
            return

        eans_exits = {item[0] for item in self.generator.eans_and_skus}
        skus_exist = {item[1] for item in self.generator.eans_and_skus}

        if (ean in eans_exits and sku in skus_exist) and (
                ean in self.manual_eans or sku in self.manual_skus or code in self.manual_code_product):
            messagebox.showwarning("Aviso",
                                   f"O EAN '{ean}', SKU '{sku}' ou código '{code}' já existem e foram desconsiderados.")

            for item in self.tree.get_children():
                item_values = self.tree.item(item, 'values')
                if item_values[0] == ean or item_values[1] == sku:
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
            return

        strategy_map = {
            "EAN": AddEANStrategy(),
            "SKU": AddSKUStrategy(),
            "Ambos(EAN e SKU)": AddBothStrategy(),
            "Full Mercado Livre": AddFullMercadoLivreStrategy(),
            "Full Amazon": AddFullAmazonStrategy(),
        }

        strategy = strategy_map.get(code_type)

        if strategy:
            strategy.add(self.generator, ean, sku, quantity, description, code, size)

        self.tree.insert("", tk.END, values=(ean, sku, quantity, description, code, size))

        self.manual_eans.append(ean)
        self.manual_skus.append(sku)
        self.manual_code_product.append(code)

        for entry in [self.ean_entry, self.sku_entry, self.quantity_entry, self.description_entry,
                      self.code_product_entry, self.size_entry]:
            entry.delete(0, tk.END)

    def calculate_quantity_to_send(self, total_quantity, columns):
        if columns == 2:
            return total_quantity if total_quantity % 2 == 0 else total_quantity + 1
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
            ean, sku, quantity_str, description, code_product, size = item_values

            if not quantity_str.isdigit():
                messagebox.showwarning("Aviso", f"Quantidade inválida na linha: {item_values}. Ignorando.")
                continue

            quantity = int(quantity_str)

            if selected_type == "EAN" and not ean:
                continue
            if selected_type == "SKU" and not sku:
                continue

            label_format = self.label_format.get()
            columns = 2 if label_format == "2-Colunas" else 1

            adjusted_quantity = self.calculate_quantity_to_send(quantity, columns)
            labels_data.append((ean, sku, adjusted_quantity, description, code_product, size))

        if not labels_data:
            messagebox.showerror("Erro", "Nenhum dado válido para gerar etiquetas.")
            return

        tag_msg = "A impressão será de uma etiqueta 80x30." if columns == 1 else "A impressão será de uma etiqueta 100x25."
        messagebox.showinfo("Informação", tag_msg)

        self.generator.eans_and_skus.clear()

        for ean, sku, adjusted_quantity, description, code_product, size in labels_data:
            if selected_type == "EAN":
                self.generator.add_ean_sku(ean, "", adjusted_quantity, "")
            elif selected_type == "SKU":
                self.generator.add_ean_sku("", sku, adjusted_quantity, "")
            elif selected_type == "Full Mercado Livre":
                self.generator.add_sku_code_description_tag_full("", sku, adjusted_quantity, description, code_product,
                                                                 size)
            elif selected_type == "Full Amazon":
                self.generator.add_sku_code_description_tag_full("", sku, adjusted_quantity, description, code_product,
                                                                 "")
            else:
                self.generator.add_ean_sku(ean, sku, adjusted_quantity, description)

        self.generator.set_label_format(label_format, selected_type)
        self.zpl_code = self.generator.generate_zpl()

        if self.zpl_code:
            self.label_text.config(state="normal")
            self.label_text.delete("1.0", tk.END)
            self.label_text.insert("1.0", self.zpl_code)
            self.label_text.config(state="disabled")
            self.print_button_zpl.config(state=tk.NORMAL)
            self.print_button_pdf.config(state=tk.NORMAL)
            self.pdf_button.config(state=tk.NORMAL)
            messagebox.showinfo("Sucesso", "Código ZPL gerado com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao gerar o código ZPL.")
            self.print_button_zpl.config(state=tk.DISABLED)
            self.print_button_pdf.config(state=tk.DISABLED)
            self.pdf_button.config(state=tk.DISABLED)

    def save_zpl(self):
        if not self.zpl_code:
            messagebox.showerror("Erro", "Nenhum código ZPL gerado. Gere antes de salvar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".zpl",
                                                 initialfile="Etiqueta",
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

    def copy_zpl(self, event=None):
        for item in self.tree.selection():
            self.tree.selection_remove(item)

        zpl_content = self.label_text.get("1.0", tk.END).strip()
        if zpl_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(zpl_content)
            self.root.update()
            messagebox.showinfo("Copiado!", "Código ZPL copiado para a área de transferência.")
        else:
            messagebox.showwarning("Aviso", "Não há código ZPL para copiar.")

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
        if screen_name == "Impressao ZPL":
            ZPLManualView(self.root, self.printer_service, self.zebra_labelary_api_service)
        else:
            messagebox.showinfo("Info", f"Tela '{screen_name}' não implementada.")

    def toggle_select_all(self):
        if self.select_all_var.get():
            self.select_all_rows()
        else:
            self.tree.selection_remove(self.tree.get_children())

    def add_product_to_barcode(self, ean, sku, quantity):
        self.tree.insert("", tk.END, values=(ean, sku, quantity))
        self.manual_eans.append(ean)
        self.manual_skus.append(sku)

    def update_preview(self):
        """
            Gera a imagem a partir do ZPL (via Labelary) e exibe no Label de preview.
        """
        if not self.zpl_code:
            return

        selected_label_format = self.label_format.get()
        self.zebra_labelary_api_service.update_preview(self.zpl_code, selected_label_format, self.preview_image_label)

    def generate_pdf(self):
        if not self.zpl_code:
            messagebox.showerror("Erro", "Nenhum código ZPL gerado. Gere antes de salvar.")
            return

        pdf_data = self.zebra_labelary_api_service.generate_pdf(
            self.zpl_code,
            LabelFormatConstants.PRINTER_DENSITY_8DPMM,
            LabelFormatConstants.LABEL_DIMENSIONS_5X25,
            LabelFormatConstants.LABEL_INDEX_0
        )

        if pdf_data:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     initialfile="Etiqueta",
                                                     filetypes=[("Arquivo PDF", "*.pdf")])
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(pdf_data)
                messagebox.showinfo("Sucesso", f"Arquivo PDF salvo em: {file_path}")
                self.pdf_button.config(state="normal")
        else:
            messagebox.showerror("Erro", "Falha ao gerar o PDF da etiqueta.")

    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)

    def set_quantity(self, item):
        new_quantity = self.entry.get().strip()
        if new_quantity.isdigit():
            self.tree.set(item, column="Quantidade", value=new_quantity)
            self.quantity_window.destroy()
        else:
            messagebox.showerror("Erro", "Quantidade inválida. Por favor, insira um número válido.")
            
    def remove_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = selected_item[0]

        self.remove_window = tk.Toplevel(self.root)
        self.remove_window.title("Remover Item")
        self.remove_window.geometry("400x200")
        self.remove_window.grab_set()
        DialogCenter.center_window(self.remove_window)

        label = tk.Label(self.remove_window, text="Tem certeza que deseja remover este item?")
        label.pack(pady=10)

        button_frame = tk.Frame(self.remove_window)
        button_frame.pack(pady=10)

        ok_button = tk.Button(button_frame, text="Remover", command=lambda: self.confirm_removal(item))
        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.remove_window.destroy)

        ok_button.pack(side="left", padx=10)
        cancel_button.pack(side="right", padx=10)

    def confirm_removal(self, item):
        self.tree.delete(item)
        self.remove_window.destroy()

    def deselect_on_click_outside(self, event):
        if not (self.tree.winfo_containing(event.x_root, event.y_root) or self.label_text.winfo_containing(event.x_root,
                                                                                                           event.y_root)):
            self.tree.selection_remove(self.tree.selection())
            print("Seleção removida da tabela, clicado fora.")

    def edit_label_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = selected_item[0]
        current_values = self.tree.item(item, "values")

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Editar Dados da Etiqueta")
        self.edit_window.geometry("600x350")
        self.edit_window.grab_set()

        labels = ["EAN", "SKU", "Quantidade", "Descrição", "Código", "Tamanho"]
        self.edit_entries = {}

        for idx, label_text in enumerate(labels):
            label = tk.Label(self.edit_window, text=label_text + ":")
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            entry = tk.Entry(self.edit_window, width=50)
            entry.insert(0, current_values[idx])
            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.edit_entries[label_text] = entry

        button_frame = tk.Frame(self.edit_window)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=15)

        ok_button = tk.Button(button_frame, text="Salvar", command=lambda: self.save_edited_label_data(item))
        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.edit_window.destroy)

        ok_button.pack(side="left", padx=10)
        cancel_button.pack(side="right", padx=10)

    def save_edited_label_data(self, item):
        new_values = []
        for field in ["EAN", "SKU", "Quantidade", "Descrição", "Código", "Tamanho"]:
            value = self.edit_entries[field].get().strip()
            if field == "Quantidade" and not value.isdigit():
                messagebox.showerror("Erro", "Quantidade inválida. Por favor, insira um número válido.")
                return
            new_values.append(value)

        self.tree.item(item, values=new_values)
        self.edit_window.destroy()