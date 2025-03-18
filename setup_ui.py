import ttkbootstrap as tb
from tkinter import messagebox
from pystray import MenuItem as item, Icon
from PIL import Image, ImageTk
from src.core.database.database import Database
from src.views.barcode.barcode_screen import BarcodeScreen
import sys

def main():
    global root, is_dark_mode, theme_button, tray_icon

    root = tb.Window(themename="cosmo")
    root.style.configure("Logo.TLabel", background="#222", font=("Arial", 12), foreground="#EEE")

    root.title("Nova Tag")
    root.geometry("1460x900")

    if sys.platform.startswith("win"):
        try:
            root.iconbitmap("./nova-software-logo.ico")
        except Exception as e:
            print(f"Erro ao carregar ícone no Windows: {e}")
    elif sys.platform.startswith("linux"):
        try:
            root.iconbitmap("./nova-software-logo.png")
        except Exception as e:
            print(f"Erro ao carregar ícone no Linux: {e}")

    root.resizable(True, True)

    is_dark_mode = True

    frame = tb.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky="nsew")

    theme_button = tb.Button(frame, text="Alternar Tema", bootstyle="primary", command=toggle_theme)
    theme_button.grid(row=0, column=0, padx=10, pady=10)

    app = BarcodeScreen(root)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)
    root.bind("<F2>", toggle_theme)
    root.bind("<Control-q>", exit_application)
    root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

    Database.create_tables()
    create_tray_icon()
    root.mainloop()

def toggle_fullscreen(event=None):
    root.attributes('-fullscreen', not root.attributes('-fullscreen'))

def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

def toggle_theme(event=None):
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    new_theme = "darkly" if is_dark_mode else "flatly"
    root.style.theme_use(new_theme)

def exit_application(event=None):
    if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?", icon="warning"):
        tray_icon.stop()
        root.quit()

def minimize_to_tray():
    root.withdraw()
    tray_icon.visible = True

def restore_from_tray(icon, item):
    root.deiconify()
    tray_icon.visible = False

def create_tray_icon():
    global tray_icon

    try:
        if sys.platform.startswith("win"):
            image = Image.open("./nova-software-logo.ico")
        else:
            image = Image.open("./nova-software-logo.png")
    except Exception as e:
        print(f"Erro ao carregar imagem do ícone da bandeja: {e}")
        image = Image.new("RGB", (64, 64), color="gray")

    menu = (item('Restaurar', restore_from_tray), item('Sair', exit_application))
    tray_icon = Icon("Nova Tag", image, menu=menu)

    def run_tray():
        tray_icon.run()

    from threading import Thread
    Thread(target=run_tray, daemon=True).start()

def on_close():
    minimize_to_tray()

if __name__ == "__main__":
    main()
