import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from src.core.database.repositories.product_repo import ProductRepository

class ProductScreen:
    def __init__(self, parent, barcode_screen):
        self.parent = parent
        self.barcode_screen = barcode_screen

        self.window = tb.Toplevel(parent, size=(1440, 900))
        self.window.title("Nova Tag - Produtos")

        if sys.platform.startswith("win"):
            try:
                self.window.iconbitmap("./nova-software-logo.ico")
            except Exception as e:
                print(f"Erro ao carregar ícone no Windows: {e}")
        elif sys.platform.startswith("linux"):
            try:
                self.window.iconbitmap("@./nova-software-logo.xbm")
            except Exception as e:
                print(f"Erro ao carregar ícone no Linux: {e}")

        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_menu_bar()
        self.build_layout()
        self.minimize_main_window()
        self.load_products()

    def build_menu_bar(self):
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Configurações", menu=self.config_menu)
        self.config_menu.add_command(label="Alternar Tema", command=self.toggle_theme)

    def build_layout(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Lista de produtos
        self.tree = ttk.Treeview(main_frame, columns=("Nome", "Categoria", "EAN", "SKU", "Preço"), show="headings")
        for col in ("Nome", "Categoria", "EAN", "SKU", "Preço"):
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=200, anchor="center")
        self.tree.pack(fill='both', expand=True, side='left')

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill='x')

        self.add_to_barcode_button = ttk.Button(button_frame, text="Adicionar ao Barcode", command=self.add_to_barcode, width=20)
        self.add_to_barcode_button.pack(side="left", padx=5)

        self.search_entry = ttk.Entry(button_frame, width=30)
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.insert(0, "Buscar Produto...")
        self.search_entry.bind("<KeyRelease>", self.search_product)

    def load_products(self):
        products = ProductRepository.list_all_products()
        for product in products:
            self.tree.insert("", tk.END, values=(product['product_description'], "Categoria", product['product_ean'], product['product_sku'], f"R$ {product['product_price']}"))

    def add_to_barcode(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Nenhum produto selecionado.")
            return

        for item in selected_items:
            item_values = self.tree.item(item, "values")
            ean, sku = item_values[2], item_values[3]
            quantity = simpledialog.askinteger("Quantidade", f"Insira a quantidade de etiquetas para {item_values[0]}:",
                                               minvalue=1)
            if quantity:
                self.barcode_screen.add_product_to_barcode(ean, sku, quantity)

        messagebox.showinfo("Sucesso", "Produtos adicionados ao Barcode com sucesso!")

    def search_product(self, event):
        query = self.search_entry.get().lower()
        for item in self.tree.get_children():
            item_values = self.tree.item(item, "values")
            match = any(query in str(value).lower() for value in item_values)
            self.tree.item(item, tags=("match" if match else "nomatch"))
        self.tree.tag_configure("match", background="white")
        self.tree.tag_configure("nomatch", background="#d3d3d3")

    def toggle_theme(self):
        self.theme = "darkly" if self.theme == "flatly" else "flatly"
        self.style.theme_use(self.theme)

    def minimize_main_window(self):
        self.parent.iconify()

    def on_close(self):
        if self.parent and isinstance(self.parent, tk.Tk):
            self.parent.deiconify()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = ProductScreen(root, None)
    root.mainloop()
