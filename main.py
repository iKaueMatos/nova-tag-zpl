import os
import tkinter as tk
import threading
from dotenv import load_dotenv

from src.update.Updater import Updater
from src.utils.notification_windows_linux import NotificationWindowsLinux
from src.views.barcode_label_app import BarcodeLabelApp

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
INSTALLER_NAME = os.getenv("INSTALLER_NAME")

def main():
    global root
    root = tk.Tk()
    root.title("Nova Tag")

    root.geometry("1440x900")
    root.configure(bg='#f0f0f0')
    root.iconbitmap("./nova-software-logo.ico")

    root.resizable(True, True)
    app = BarcodeLabelApp(root)

    threading.Thread(target=periodic_check, daemon=True).start()
    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)

    root.mainloop()

def periodic_check():
    """Verifica atualizações do GitHub periodicamente."""
    if not GITHUB_TOKEN:
        print("Erro: O token do GitHub não está configurado no arquivo .env.")
        return

    updater = Updater(repo=GITHUB_REPO, installer_name=INSTALLER_NAME, token=GITHUB_TOKEN)
    updater.check_for_update()

def toggle_fullscreen(event=None):
    """Alterna entre tela cheia e modo janela."""
    state = root.attributes('-fullscreen')
    root.attributes('-fullscreen', not state)


def exit_fullscreen(event=None):
    """Sai do modo tela cheia (pressionando ESC)."""
    root.attributes('-fullscreen', False)

if __name__ == "__main__":
    main()