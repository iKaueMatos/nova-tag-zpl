import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ProductScreen:
    def __init__(self, parent, barcode_screen):
        self.parent = parent
        self.barcode_screen = barcode_screen

        self.window = tk.Toplevel(parent)
        self.window.title("Nova Tag - Produtos")
        self.window.geometry("1440x900")
        self.window.iconbitmap("./nova-software-logo.ico")
        self.window.resizable(True, True)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.build_menu_bar()
        self.build_layout()
        self.minimize_main_window()

    def on_close(self):
        """Reexibe a janela principal ao fechar a secundária"""
        self.parent.deiconify()
        self.window.destroy()

    def build_menu_bar(self):
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Configurações", menu=self.config_menu)
        self.config_menu.add_command(label="Adicionar Produto", command=self.add_product)
        self.config_menu.add_command(label="Limpar Lista", command=self.clear_product_list)

    def build_layout(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.tree = ttk.Treeview(main_frame, columns=("Nome", "Categoria", "EAN", "SKU", "Preço"), show="headings")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("EAN", text="EAN")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Preço", text="Preço")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.add_button = ttk.Button(button_frame, text="Adicionar Produto", command=self.add_product)
        self.add_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(button_frame, text="Limpar Lista", command=self.clear_product_list)
        self.clear_button.pack(side="left", padx=5)

        self.add_sample_data()

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def add_sample_data(self):
        products = [
            ("Produto 1", "Categoria A", "1234567890123", "SKU001", "$10.00"),
            ("Produto 2", "Categoria B", "2345678901234", "SKU002", "$20.00"),
            ("Produto 3", "Categoria C", "3456789012345", "SKU003", "$30.00"),
        ]
        for product in products:
            self.tree.insert("", tk.END, values=product)

    def add_product(self):
        name = simpledialog.askstring("Adicionar Produto", "Nome do Produto:")
        if not name:
            return

        category = simpledialog.askstring("Adicionar Produto", "Categoria:")
        if not category:
            return

        ean = simpledialog.askstring("Adicionar Produto", "EAN:")
        if not ean:
            return

        sku = simpledialog.askstring("Adicionar Produto", "SKU:")
        if not sku:
            return

        price = simpledialog.askstring("Adicionar Produto", "Preço:")
        if not price:
            return

        self.tree.insert("", tk.END, values=(name, category, ean, sku, price))
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")

    def clear_product_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        messagebox.showinfo("Sucesso", "Lista de produtos limpa.")

    def minimize_main_window(self):
        self.parent.iconify()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductScreen(root, None)
    root.mainloop()
