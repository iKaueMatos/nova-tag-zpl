import os
import sys
import requests
import time
import subprocess
import tkinter as tk
from tkinter import ttk
import threading

from src.utils.notification_windows_linux import NotificationWindowsLinux

class Updater:
    def __init__(self, repo, installer_name, token):
        """Inicializa o atualizador com configurações do repositório"""
        self.github_repo = repo
        self.installer_name = installer_name
        self.token = token
        self.version_file = os.path.join(os.getenv("APPDATA"), "Novatag", "version.txt")
        self.temp_folder = os.getenv("TEMP")
        self.installer_path = os.path.join(self.temp_folder, self.installer_name)

    def get_latest_version(self):
        """ Obtém a versão mais recente disponível no GitHub Releases """
        url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        headers = {"Authorization": f"token {self.token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            latest_version = response.json()["tag_name"]
            NotificationWindowsLinux.show_update_notification(latest_version)
            return latest_version
        else:
            NotificationWindowsLinux.show_error_notification("Não foi possível obter a versão mais recente.")
            print("Erro ao obter a versão mais recente:", response.text)
            return None

    def get_current_version(self):
        """ Lê a versão do aplicativo instalada """
        if not os.path.exists(self.version_file):
            return "0.0.0"

        with open(self.version_file, "r") as file:
            return file.read().strip()

    def show_progress_window(self):
        """ Exibe uma janela gráfica com barra de progresso """
        self.root = tk.Tk()
        self.root.title("Atualizando...")

        ttk.Label(self.root, text="Baixando atualização...").pack(pady=10)
        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.root.geometry("350x120")
        self.root.resizable(False, False)

        return self.root, self.progress

    def download_installer(self):
        """ Faz o download do novo instalador do GitHub Releases """
        latest_version = self.get_latest_version()
        if not latest_version:
            return None

        url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        headers = {"Authorization": f"token {self.token}"}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Erro ao obter informações da release:", response.text)
            return None

        assets = response.json().get("assets", [])
        installer_url = None
        for asset in assets:
            # Verifique se o nome do arquivo do instalador corresponde
            if self.installer_name in asset["name"]:
                installer_url = asset["browser_download_url"]
                break

        if not installer_url:
            print("Erro: Arquivo do instalador não encontrado na release.")
            return None

        response = requests.get(installer_url, stream=True, headers=headers)
        total_size = int(response.headers.get("content-length", 0))

        if response.status_code == 200:
            root, progress = self.show_progress_window()
            with open(self.installer_path, "wb") as file:
                downloaded = 0
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                    downloaded += len(chunk)
                    progress["value"] = (downloaded / total_size) * 100
                    root.update_idletasks()

            root.destroy()
            NotificationWindowsLinux.show_download_notification()
            return self.installer_path
        else:
            print("Erro ao baixar o novo instalador.")
            return None

    def run_installer(self):
        """ Executa o instalador e fecha a aplicação atual """
        NotificationWindowsLinux.show_install_notification()
        time.sleep(2)

        if sys.platform == "win32":
            subprocess.Popen([self.installer_path, "/SILENT"], shell=True)
        else:
            subprocess.Popen(["xdg-open", self.installer_path])  # Linux

        print("Fechando o aplicativo para atualização...")
        sys.exit()

    def check_for_update(self):
        """ Verifica se há uma nova versão disponível e inicia a atualização """
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        if latest_version and latest_version != current_version:
            print(f"Nova versão disponível: {latest_version} (Atual: {current_version})")
            NotificationWindowsLinux.show_update_notification(latest_version)

            installer_path = self.download_installer()
            if installer_path:
                self.run_installer()
        else:
            print("Nenhuma atualização necessária.")

    def periodic_check(self):
        """ Verifica atualizações periodicamente """
        self.check_for_update()
        threading.Timer(3600, self.periodic_check).start()