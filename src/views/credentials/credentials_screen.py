from PIL._tkinter_finder import tk
from tkinter import messagebox
from src.service.omie.omie_list_products import OmieListProducts
from src.core.database.repositories.credentials_repo import CredentialsRepository

class CredentialsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciar Credenciais da API")
        self.root.geometry("1440x900")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Empresa:").pack()
        self.company_entry = tk.Entry(self.root)
        self.company_entry.pack()

        tk.Label(self.root, text="App Key:").pack()
        self.app_key_entry = tk.Entry(self.root)
        self.app_key_entry.pack()

        tk.Label(self.root, text="App Secret:").pack()
        self.app_secret_entry = tk.Entry(self.root, show="*")
        self.app_secret_entry.pack()

        tk.Label(self.root, text="Client Tax:").pack()
        self.client_tax_entry = tk.Entry(self.root)
        self.client_tax_entry.pack()

        tk.Label(self.root, text="Tax Scenario:").pack()
        self.tax_scenario_entry = tk.Entry(self.root)
        self.tax_scenario_entry.pack()

        tk.Label(self.root, text="Stock Location:").pack()
        self.stock_location_entry = tk.Entry(self.root)
        self.stock_location_entry.pack()
        tk.Button(self.root, text="Salvar", command=self.save_credentials).pack(pady=10)

    def save_credentials(self):
        company = self.company_entry.get()
        app_key = self.app_key_entry.get()
        app_secret = self.app_secret_entry.get()
        client_tax = self.client_tax_entry.get()
        tax_scenario = self.tax_scenario_entry.get()
        stock_location = self.stock_location_entry.get()

        CredentialsRepository.insert_credentials(company, app_key, app_secret, client_tax, tax_scenario, stock_location)
        messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")

    def fetch_products(self):
        company = self.company_entry.get()
        app_key = self.app_key_entry.get()
        app_secret = self.app_secret_entry.get()

        if not company or not app_key or not app_secret:
            messagebox.showerror("Erro", "Empresa, App Key e App Secret são obrigatórios.")
            return

        try:
            omie_service = OmieListProducts(company)
            products = omie_service.all()
            print(products)
            messagebox.showinfo("Sucesso", "Produtos buscados e salvos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao buscar produtos: {e}")