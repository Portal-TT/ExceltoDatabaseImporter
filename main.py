import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pyodbc
import threading

# Configuración de la conexión global
db_config = {
    "server": "",
    "database": "",
    "user": "",
    "password": "",
    "trusted_connection": "no",
}

# Query para crear tabla Historial
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

# Query para crear tabla Reservaciones
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

def update_status(message):
    """Actualizar mensajes de estado en la interfaz."""
    status_label.config(text=message)
    root.update_idletasks()

# Conexión a SQL Server
def connect_to_db():
    try:
        update_status("Intentando conectar a la base de datos...")
        connection_string = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
        )
        if db_config["trusted_connection"].lower() == "yes":
            connection_string += "Trusted_Connection=yes;"
        else:
            connection_string += f"UID={db_config['user']};PWD={db_config['password']};"

        connection = pyodbc.connect(connection_string)
        update_status("Conexión exitosa a la base de datos.")
        return connection
    except Exception as e:
        update_status(f"Error de conexión: {e}")
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None

# Crear tablas
def create_tables():
    connection = connect_to_db()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_HISTORIAL_TABLE)
        cursor.execute(CREATE_RESERVACIONES_TABLE)
        connection.commit()
        update_status("Tablas creadas/verificadas exitosamente.")
        return True
    except Exception as e:
        update_status(f"Error al crear/verificar tablas: {e}")
        messagebox.showerror("Error", "No se pudo crear/verificar las tablas.")
        return False
    finally:
        connection.close()

# Cargar archivo y mostrar en tabla
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel o CSV", "*.xls *.xlsx *.csv")])
    if not file_path:
        update_status("No se seleccionó ningún archivo.")
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

        for row in tree.get_children():
            tree.delete(row)

        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        update_status(f"Archivo '{file_name}' cargado correctamente.")
        save_button.config(state=tk.NORMAL)
        save_button.config(command=lambda: threading.Thread(target=save_to_db, args=(df, file_name)).start())
    except Exception as e:
        update_status(f"Error al cargar archivo: {e}")
        messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

# Verificar archivo en historial
def is_file_in_historial(file_name):
    connection = connect_to_db()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Historial WHERE nombre_archivo = ?", file_name)
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        update_status(f"Error al verificar historial: {e}")
        return False
    finally:
        connection.close()

# Guardar archivo en historial
def save_to_historial(file_name):
    connection = connect_to_db()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Historial (nombre_archivo) VALUES (?)", file_name)
        connection.commit()
        update_status(f"Archivo '{file_name}' guardado en historial.")
    except Exception as e:
        update_status(f"Error al guardar en historial: {e}")
    finally:
        connection.close()

# Guardar datos en la base de datos
def save_to_db(df, file_name):
    connection = connect_to_db()
    if connection is None:
        update_status("No se pudo conectar a la base de datos. Proceso cancelado.")
        return

    cursor = connection.cursor()
    try:
        update_status("Iniciando inserción de datos...")
        for _, row in df.iterrows():
            cleaned_row = {col: (str(row[col]) if pd.notna(row[col]) else None) for col in df.columns}
            cursor.execute(
                """
                INSERT INTO Reservaciones (
                    fecha, hora, estado, turno, personas, origen, prescriptor,
                    fecha_anadida, hora_anadida, establecimiento, tipo, nombre,
                    apellidos, mesa, zona, anotado_por, codigo, telefono,
                    grupo, referencia, codigo_referencia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                cleaned_row["Fecha"],
                cleaned_row["Hora"],
                cleaned_row["Estado"],
                cleaned_row["Turno"],
                cleaned_row["Personas"],
                cleaned_row["Origen"],
                cleaned_row["Prescriptor"],
                cleaned_row["Fecha Añadida"],
                cleaned_row["Hora Añadida"],
                cleaned_row["Establecimiento"],
                cleaned_row["Tipo"],
                cleaned_row["Nombre"],
                cleaned_row["Apellidos"],
                cleaned_row["Mesa"],
                cleaned_row["Zona"],
                cleaned_row["Anotado por"],
                cleaned_row["Código"],
                cleaned_row["Teléfono"],
                cleaned_row["Grupo"],
                cleaned_row["Referencia"],
                cleaned_row["Código de referencia"],
            )

        connection.commit()
        save_to_historial(file_name)
        update_status("Datos guardados correctamente.")
        messagebox.showinfo("Éxito", "Datos guardados correctamente en la base de datos.")
    except Exception as e:
        update_status(f"Error al guardar datos: {e}")
        messagebox.showerror("Error", f"No se pudieron guardar los datos: {e}")
    finally:
        connection.close()

# Configurar conexión
def configure_connection():
    def save_config():
        db_config["server"] = server_var.get().strip()
        db_config["database"] = database_var.get().strip()
        db_config["user"] = user_var.get().strip()
        db_config["password"] = password_var.get().strip()
        if not db_config["server"] or not db_config["database"]:
            messagebox.showwarning("Advertencia", "Servidor y Base de Datos son obligatorios.")
            return
        update_status(f"Conexión configurada: {db_config['server']}/{db_config['database']}")
        load_button.config(state=tk.NORMAL)
        create_tables()
        config_window.destroy()

    config_window = tk.Toplevel(root)
    config_window.title("Configurar Conexión")
    config_window.geometry("400x400")

    ttk.Label(config_window, text="Servidor:").pack(pady=5)
    server_var = tk.StringVar()
    ttk.Entry(config_window, textvariable=server_var).pack(pady=5)

    ttk.Label(config_window, text="Base de Datos:").pack(pady=5)
    database_var = tk.StringVar()
    ttk.Entry(config_window, textvariable=database_var).pack(pady=5)

    ttk.Label(config_window, text="Usuario:").pack(pady=5)
    user_var = tk.StringVar()
    ttk.Entry(config_window, textvariable=user_var).pack(pady=5)

    ttk.Label(config_window, text="Contraseña:").pack(pady=5)
    password_var = tk.StringVar()
    ttk.Entry(config_window, textvariable=password_var, show="*").pack(pady=5)

    ttk.Button(config_window, text="Guardar", command=save_config).pack(pady=20)

# Interfaz principal
root = tk.Tk()
root.title("Transat - Cargar Archivo a SQL Server")
root.geometry("800x600")

connection_label = ttk.Label(root, text="No hay conexión configurada.", foreground="red")
connection_label.pack(pady=5)

config_button = ttk.Button(root, text="Configurar Conexión", command=configure_connection)
config_button.pack(pady=10)

load_button = ttk.Button(root, text="Cargar Archivo", command=load_file, state=tk.DISABLED)
load_button.pack(pady=10)

tree_frame = ttk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree = ttk.Treeview(tree_frame, xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

status_label = ttk.Label(root, text="", foreground="blue")
status_label.pack(pady=5)

save_button = ttk.Button(root, text="Guardar en BD", state=tk.DISABLED)
save_button.pack(pady=10)

root.mainloop()
