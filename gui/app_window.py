import tkinter as tk
from tkinter import ttk
from utils.file_handler import load_file
from database.setup import setup_database

def start_app(config):
    """Ventana principal para cargar y guardar archivos."""
    root = tk.Tk()
    root.title("Cargar Archivo a SQL Server")
    root.geometry("800x600")

    # Botón para cargar el archivo
    ttk.Button(root, text="Cargar Archivo", command=lambda: load_file(tree, progress)).pack(pady=10)

    # Tabla para mostrar los datos cargados
    tree = ttk.Treeview(root, height=15)
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Barra de progreso
    progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
    progress.pack(pady=10)

    # Configurar base de datos
    setup_database(config)

    root.mainloop()
