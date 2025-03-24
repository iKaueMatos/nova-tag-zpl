# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
import os
from tkinter import messagebox
import tkinter as tk
from plyer import notification

class NotificationWindowsLinux:
    def __init__(self, icon_filename="nova-software-logo.ico"):
        self.icon_path = os.path.abspath(os.path.join(os.getcwd(), icon_filename))

    @staticmethod
    def show_notification(title, message, timeout=5):
        """Exibe uma notificação no Windows ou Linux com ícone."""
        icon_path = os.path.abspath(os.path.join(os.getcwd(), "nova-software-logo.ico"))

        if not os.path.exists(icon_path):
            print("Aviso: O ícone não foi encontrado.")
            icon_path = None

        notification.notify(
            title=title,
            message=message,
            timeout=timeout,
            app_icon=icon_path
        )

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)

    @staticmethod
    def show_update_notification(latest_version):
        """Exibe uma notificação sobre a atualização disponível."""
        title = "Nova atualização disponível"
        message = f"Uma nova versão ({latest_version}) está disponível. Clique para atualizar."
        NotificationWindowsLinux.show_notification(title, message)

    @staticmethod
    def show_download_notification():
        """Exibe uma notificação quando o download está sendo feito."""
        title = "Baixando Atualização"
        message = "O download da atualização está em andamento..."
        NotificationWindowsLinux.show_notification(title, message)

    @staticmethod
    def show_install_notification():
        """Exibe uma notificação informando sobre a instalação da atualização."""
        title = "Instalando Atualização"
        message = "A instalação da nova versão começará em breve."
        NotificationWindowsLinux.show_notification(title, message)

    @staticmethod
    def show_error_notification(error_message):
        """Exibe uma notificação de erro."""
        title = "Erro ao Atualizar"
        message = f"Ocorreu um erro: {error_message}"
        NotificationWindowsLinux.show_notification(title, message)
