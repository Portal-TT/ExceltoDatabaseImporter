import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pyodbc
import threading

# Configuración de conexión a SQL Server
DB_CONFIG = {
    'server': 'LAAM-CUNSIS4',  # Cambia al nombre de tu servidor
    'database': 'ReservacionesDB',  # Cambia al nombre de tu base de datos
    'trusted_connection': 'yes'
}

# Conexión a SQL Server
def connect_to_db():
    try:
        print("Intentando conectar a la base de datos...")
        progress['value'] = 33  # Un tercio de la barra llena
        root.update_idletasks()
        
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        print("Conexión exitosa a la base de datos.")
        progress['value'] = 50  # Mitad de la barra llena
        root.update_idletasks()
        return connection
    except Exception as e:
        print(f"Error de conexión: {e}")
        progress['value'] = 0  # Reiniciar barra en caso de error
        root.update_idletasks()
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None

# Guardar los datos en la base de datos
def save_to_db(df):
    connection = connect_to_db()
    if connection is None:
        print("No se pudo conectar a la base de datos. Proceso cancelado.")
        return

    cursor = connection.cursor()
    try:
        print("Iniciando inserción de datos en la base de datos...")
        progress['value'] = 75  # 3/4 de la barra llena
        root.update_idletasks()

        progress['maximum'] = len(df) + 75  # Máximo de la barra ajustado al total de filas
        for i, row in df.iterrows():
            cleaned_row = {col: (str(row[col]) if pd.notna(row[col]) else None) for col in df.columns}
            print(f"Insertando fila {i + 1}: {cleaned_row}")  # Log de la fila que se está insertando

            cursor.execute("""
                INSERT INTO Reservaciones (
                    fecha, hora, estado, turno, personas, origen, prescriptor,
                    fecha_anadida, hora_anadida, establecimiento, tipo, nombre,
                    apellidos, mesa, zona, anotado_por, codigo, telefono,
                    grupo, referencia, codigo_referencia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            cleaned_row['Fecha'], cleaned_row['Hora'], cleaned_row['Estado'], cleaned_row['Turno'],
            cleaned_row['Personas'], cleaned_row['Origen'], cleaned_row['Prescriptor'],
            cleaned_row['Fecha Añadida'], cleaned_row['Hora Añadida'], cleaned_row['Establecimiento'],
            cleaned_row['Tipo'], cleaned_row['Nombre'], cleaned_row['Apellidos'], cleaned_row['Mesa'],
            cleaned_row['Zona'], cleaned_row['Anotado por'], cleaned_row['Código'], cleaned_row['Teléfono'],
            cleaned_row['Grupo'], cleaned_row['Referencia'], cleaned_row['Código de referencia'])
            
            progress['value'] = 75 + i + 1  # Incrementar progresivamente
            root.update_idletasks()  # Refrescar la GUI
        
        connection.commit()
        print("Datos guardados correctamente en la base de datos.")
        progress['value'] = 100  # Barra completa
        root.update_idletasks()
        messagebox.showinfo("Éxito", "Datos guardados correctamente en la base de datos.")
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
        messagebox.showerror("Error al Guardar", f"No se pudieron guardar los datos:\n{e}")
    finally:
        connection.close()
        print("Conexión cerrada.")
        progress['value'] = 0  # Reiniciar barra de progreso

# Cargar datos en la tabla visual
def display_table(df):
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    for column in df.columns:
        tree.heading(column, text=column)
        tree.column(column, width=100)

    for row in tree.get_children():
        tree.delete(row)

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# Función para cargar el archivo
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel o CSV", "*.xls *.xlsx *.csv")])
    if not file_path:
        print("No se seleccionó ningún archivo.")
        return

    try:
        if file_path.endswith('.csv'):
            print(f"Cargando archivo CSV: {file_path}")
            df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')  # Ajustar delimitador si es necesario
        else:
            print(f"Cargando archivo Excel: {file_path}")
            df = pd.read_excel(file_path, engine='openpyxl')

        print("Archivo cargado correctamente. Vista previa de los datos:")
        print(df.head())

        display_table(df)
        save_button.config(state=tk.NORMAL)
        save_button.config(command=lambda: threading.Thread(target=save_to_db, args=(df,)).start())
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        messagebox.showerror("Error al Cargar", f"No se pudo cargar el archivo:\n{e}")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Cargar Archivo a SQL Server")

# Botón para cargar el archivo
load_button = tk.Button(root, text="Cargar Archivo", command=load_file)
load_button.pack(pady=10)

# Tabla para mostrar los datos cargados
tree = ttk.Treeview(root, height=10)
tree.pack(pady=10)

# Barra de progreso
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=10)

# Botón para guardar los datos (deshabilitado inicialmente)
save_button = tk.Button(root, text="Guardar en BD", state=tk.DISABLED)
save_button.pack(pady=10)

# Iniciar la aplicación
root.mainloop()
