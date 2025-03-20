# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import threading
from src.infra.repositories.credentials_repo import CredentialsRepository
from src.infra.omie.omie_list_products import OmieListProducts
from src.infra.repositories.product_repo import ProductRepository
from src.views.product.product_screen import ProductScreen

class CredentialsScreen:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Gerenciar Credenciais da API")
        self.window.geometry("800x600")

        if sys.platform.startswith("win"):
            try:
                self.window.iconbitmap("./nova-software-logo.ico")
            except Exception as e:
                print(f"Erro ao carregar ícone no Windows: {e}")
        elif sys.platform.startswith("linux"):
            try:
                self.window.iconbitmap("@./nova-software-logo.png")
            except Exception as e:
                print(f"Erro ao carregar ícone no Linux: {e}")

        self.create_widgets()
        self.load_credentials()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="10")
        frame.grid(row=0, column=0, sticky="nsew")

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        ttk.Label(frame, text="Empresa:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.company_entry = ttk.Entry(frame)
        self.company_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="App Key:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.app_key_entry = ttk.Entry(frame)
        self.app_key_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="App Secret:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.app_secret_entry = ttk.Entry(frame, show="*")
        self.app_secret_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.button_frame = ttk.Frame(frame)
        self.button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.save_button = ttk.Button(self.button_frame, text="Salvar", command=self.save_credentials)
        self.save_button.pack(side="left", padx=5)

        self.edit_button = ttk.Button(self.button_frame, text="Editar", command=self.enable_editing, state=tk.DISABLED)
        self.edit_button.pack(side="left", padx=5)

        link_frame = ttk.Frame(frame)
        link_frame.grid(row=8, column=0, columnspan=2, pady=10)
        link_label = ttk.Label(link_frame, text="Clique aqui para obter a chave de acesso para integrações de API", foreground="blue", cursor="hand2")
        link_label.pack()
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://ajuda.omie.com.br/pt-BR/articles/499061-obtendo-a-chave-de-acesso-para-integracoes-de-api"))

    def load_credentials(self):
        company = self.company_entry.get()
        credentials = CredentialsRepository.get_credentials(company)
        if credentials:
            self.app_key_entry.insert(0, credentials['app_key'])
            self.app_secret_entry.insert(0, credentials['app_secret'])
            self.disable_editing()

    def disable_editing(self):
        self.company_entry.config(state="disabled")
        self.app_key_entry.config(state="disabled")
        self.app_secret_entry.config(state="disabled")
        self.save_button.config(state="disabled")
        self.edit_button.config(state="normal")

    def enable_editing(self):
        self.company_entry.config(state="normal")
        self.app_key_entry.config(state="normal")
        self.app_secret_entry.config(state="normal")
        self.save_button.config(state="normal")
        self.edit_button.config(state="disabled")

    def save_credentials(self):
        company = self.company_entry.get()
        app_key = self.app_key_entry.get()
        app_secret = self.app_secret_entry.get()

        CredentialsRepository.insert_credentials(company, app_key, app_secret)
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")
        threading.Thread(target=self.fetch_and_save_products, args=(company,), daemon=True).start()

    def fetch_and_save_products(self, company):
        try:
            omie_products = OmieListProducts(company).all()
            for product in omie_products:
                ProductRepository.insert_product(
                    product['codInt_familia'],
                    product['descricao'],
                    product['ean'],
                    product['codigo'],
                    0 if product['preco'] == 0 else product['preco']
                )
            messagebox.showinfo("Sucesso", "Produtos importados e salvos com sucesso!")
            self.render_products()
        except KeyError as e:
            messagebox.showerror("Erro", f"Erro ao importar produtos: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def render_products(self):
        product_window = tk.Toplevel(self.root)
        ProductScreen(product_window, self.root)