import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pyodbc
import threading

# Variables globales para la configuración de la conexión
db_config = {
    "server": "",
    "database": "",
    "trusted_connection": "yes",
}

# Query para crear la tabla 'Historial'
CREATE_HISTORIAL_TABLE = """
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='Historial' AND xtype='U'
)
CREATE TABLE Historial (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre_archivo VARCHAR(255),
    fecha_subida DATETIME DEFAULT GETDATE()
);
"""

# Query para crear la tabla 'Reservaciones'
CREATE_RESERVACIONES_TABLE = """
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='Reservaciones' AND xtype='U'
)
CREATE TABLE Reservaciones (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha VARCHAR(100),
    hora VARCHAR(50),
    estado VARCHAR(50),
    turno VARCHAR(50),
    personas VARCHAR(50),
    origen VARCHAR(50),
    prescriptor VARCHAR(150),
    fecha_anadida VARCHAR(50),
    hora_anadida VARCHAR(50),
    establecimiento VARCHAR(150),
    tipo VARCHAR(50),
    nombre VARCHAR(150),
    apellidos VARCHAR(150),
    mesa VARCHAR(50),
    zona VARCHAR(150),
    anotado_por VARCHAR(150),
    codigo VARCHAR(50),
    telefono VARCHAR(50),
    grupo VARCHAR(50),
    referencia VARCHAR(150),
    codigo_referencia VARCHAR(50)
);
"""

# Conexión a SQL Server
def connect_to_db():
    try:
        print("Intentando conectar a la base de datos...")
        progress["value"] = 33  # Un tercio de la barra llena
        root.update_idletasks()

        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"Trusted_Connection={db_config['trusted_connection']};"
        )
        print("Conexión exitosa a la base de datos.")
        progress["value"] = 50  # Mitad de la barra llena
        root.update_idletasks()
        return connection
    except Exception as e:
        print(f"Error de conexión: {e}")
        progress["value"] = 0  # Reiniciar barra en caso de error
        root.update_idletasks()
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None

# Crear tablas 'Historial' y 'Reservaciones' si no existen
def create_tables():
    connection = connect_to_db()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        # Crear tabla 'Historial'
        cursor.execute(CREATE_HISTORIAL_TABLE)
        # Crear tabla 'Reservaciones'
        cursor.execute(CREATE_RESERVACIONES_TABLE)
        connection.commit()
        print("Tablas 'Historial' y 'Reservaciones' creadas/verificadas exitosamente.")
        return True
    except Exception as e:
        print(f"Error al crear/verificar las tablas: {e}")
        messagebox.showerror("Error", "No se pudo crear/verificar las tablas requeridas.")
        return False
    finally:
        connection.close()

# Configurar conexión a SQL Server
def configure_connection():
    def save_config():
        db_config["server"] = server_var.get().strip()
        db_config["database"] = database_var.get().strip()

        if not db_config["server"] or not db_config["database"]:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        connection_label.config(
            text=f"Conexión configurada: Server={db_config['server']}, DB={db_config['database']}",
            foreground="green",
        )
        load_button.config(state=tk.NORMAL)

        # Crear las tablas 'Historial' y 'Reservaciones'
        create_tables()
        config_window.destroy()

    config_window = tk.Toplevel(root)
    config_window.title("Configurar Conexión")
    config_window.geometry("400x250")

    ttk.Label(config_window, text="Servidor:").pack(pady=5)
    server_var = tk.StringVar(value=db_config["server"])
    ttk.Entry(config_window, textvariable=server_var, width=40).pack(pady=5)

    ttk.Label(config_window, text="Base de Datos:").pack(pady=5)
    database_var = tk.StringVar(value=db_config["database"])
    ttk.Entry(config_window, textvariable=database_var, width=40).pack(pady=5)

    ttk.Button(config_window, text="Guardar", command=save_config).pack(pady=20)

# Resto del código permanece igual...


# Cargar archivo y mostrar en tabla
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel o CSV", "*.xls *.xlsx *.csv")])
    if not file_path:
        print("No se seleccionó ningún archivo.")
        return

    file_name = file_path.split("/")[-1]
    if is_file_in_historial(file_name):
        messagebox.showwarning("Archivo duplicado", "Este archivo ya ha sido subido previamente.")
        return

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, delimiter=";", encoding="utf-8")
        else:
            df = pd.read_excel(file_path, engine="openpyxl")

        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for column in df.columns:
            tree.heading(column, text=column)
            tree.column(column, width=100)

        # Limpiar las filas existentes
        for row in tree.get_children():
            tree.delete(row)

        # Insertar nuevas filas
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        save_button.config(state=tk.NORMAL)
        save_button.config(command=lambda: threading.Thread(target=save_to_db, args=(df, file_name)).start())
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

# Interfaz principal
root = tk.Tk()
root.title("Cargar Archivo a SQL Server")
root.geometry("800x600")

# Etiqueta para mostrar configuración de conexión
connection_label = ttk.Label(root, text="No hay conexión configurada.", foreground="red")
connection_label.pack(pady=5)

# Botón para configurar conexión
config_button = ttk.Button(root, text="Configurar Conexión", command=configure_connection)
config_button.pack(pady=10)

# Botón para cargar archivo (deshabilitado inicialmente)
load_button = ttk.Button(root, text="Cargar Archivo", command=load_file, state=tk.DISABLED)
load_button.pack(pady=10)

# Frame para agregar el scroll
tree_frame = ttk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True)

# Scrollbars para la tabla
tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

# Tabla para mostrar datos
tree = ttk.Treeview(tree_frame, height=15, xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

# Barra de progreso
progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress.pack(pady=10)

# Botón para guardar en la base de datos (deshabilitado inicialmente)
save_button = ttk.Button(root, text="Guardar en BD", state=tk.DISABLED)
save_button.pack(pady=10)

root.mainloop()
