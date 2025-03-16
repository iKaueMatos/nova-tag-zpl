import threading
import time
import ttkbootstrap as tb
from tkinter import messagebox
from tkinter import ttk
from pystray import MenuItem as item, Icon
from PIL import Image, ImageTk
from src.core.database.database import Database
from src.views.barcode.barcode_screen import BarcodeScreen
import datetime

def get_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Bom dia"
    elif current_hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def show_loading_screen():
    splash = tb.Toplevel()
    splash.overrideredirect(True)
    splash.update_idletasks()

    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    width, height = 600, 300
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")
    splash.configure(bg="#222222")

    greeting = get_greeting()

    greeting_label = tb.Label(splash, text=greeting, font=("Helvetica", 16, "bold"), style="Heading.TLabel")
    greeting_label.pack(pady=20)

    progress_bar = ttk.Progressbar(splash, orient="horizontal", length=300, mode="indeterminate", style="TProgressbar")
    progress_bar.pack(pady=15)
    progress_bar.start(10)

    info_label = tb.Label(splash, text="Carregando recursos importantes...", font=("Arial", 12), style="Logo.TLabel")
    info_label.pack(side="bottom", pady=10)

    resources = [
        "Leitura e geração de códigos de barras",
        "Gestão de inventário de produtos",
        "Relatórios de vendas e estoque",
        "Integração com sistemas de gestão"
    ]

    def load_resources():
        for resource in resources:
            info_label.config(text=f"Carregando: {resource}")
            splash.update()
            time.sleep(2)

        splash.update()
        time.sleep(5)
        splash.destroy()

    loading_thread = threading.Thread(target=load_resources, daemon=True)
    loading_thread.start()

def main():
    global root, is_dark_mode, theme_button, tray_icon

    root = tb.Window(themename="cosmo")
    root.style.configure("Logo.TLabel", background="#222", font=("Arial", 12), foreground="#EEE")

    show_loading_screen()

    root.title("Nova Tag")
    root.geometry("1440x900")
    root.iconbitmap("./nova-software-logo.ico")
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
    image = Image.open("./nova-software-logo.ico")
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
