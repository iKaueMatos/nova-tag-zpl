import sys
from cx_Freeze import setup, Executable
import os

build_exe_options = {
    "packages": ["tkinter", "pandas", "openpyxl", "reportlab"],
    "excludes": ["unittest", "email", "http", "pdb"],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

exe = Executable(
    script="main.py",
    base=base,
    icon="src/assets/icon.ico",
)

setup(
    name="ZPL Labels",
    version="1.0",
    description="Aplicativo para gerar etiquetas ZPL",
    options={"build_exe": build_exe_options},
    executables=[exe],
)
