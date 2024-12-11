import pyodbc
from tkinter import messagebox

def connect_to_db(config):
    """Conecta a la base de datos usando la configuración proporcionada."""
    try:
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection={config['trusted_connection']};"
        )
        return connection
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
        raise e
