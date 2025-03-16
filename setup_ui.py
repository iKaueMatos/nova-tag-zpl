import tkinter as tk
from tkinter import messagebox
import pystray
from pystray import MenuItem as item, Icon
from PIL import Image
from src.core.database.database import Database
from src.views.barcode.barcode_screen import BarcodeScreen


def main():
    global root, is_dark_mode, theme_colors, theme_button, tray_icon

    root = tk.Tk()
    root.title("Nova Tag")
    root.geometry("1440x900")
    root.iconbitmap("./nova-software-logo.ico")
    root.resizable(True, True)

    theme_colors = {
        "dark": {"bg": "#222", "fg": "#EEE", "btn_bg": "#333", "btn_fg": "#FFF"},
        "light": {"bg": "#EEE", "fg": "#222", "btn_bg": "#DDD", "btn_fg": "#000"}
    }

    is_dark_mode = True

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    theme_button = tk.Button(frame, text="Alternar Tema", command=toggle_theme)
    theme_button.grid(row=0, column=0, padx=10, pady=10)

    apply_theme()

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
    apply_theme()


def apply_theme():
    """Aplica o tema com base na variável is_dark_mode"""
    global theme_button
    theme = theme_colors["dark"] if is_dark_mode else theme_colors["light"]
    root.configure(bg=theme["bg"])
    theme_button.config(bg=theme["btn_bg"], fg=theme["btn_fg"])


def custom_messagebox(title, message, type="info"):
    """Exibe uma caixa de diálogo customizada."""
    theme = theme_colors["dark"] if is_dark_mode else theme_colors["light"]
    bg_color, fg_color = theme["bg"], theme["fg"]

    root.tk.call("tk", "messageBox", "-title", title, "-message", message, "-type", type, "-background", bg_color,
                 "-foreground", fg_color)


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
