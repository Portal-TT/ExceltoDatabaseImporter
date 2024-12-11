from tkinter import Toplevel, StringVar, Label, Entry, Button, messagebox, ttk

def get_connection_config():
    """Ventana para configurar la conexión a SQL Server."""
    config = {}

    def save_config():
        server = server_var.get().strip()
        database = database_var.get().strip()

        if not server or not database:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        config["server"] = server
        config["database"] = database
        config["trusted_connection"] = "yes"
        connection_window.destroy()

    # Crear ventana de configuración
    connection_window = Toplevel()
    connection_window.title("Configuración de Conexión")
    connection_window.geometry("400x250")
    connection_window.resizable(False, False)

    ttk.Style().theme_use("clam")

    Label(connection_window, text="Configurar Conexión a SQL Server", font=("Arial", 14, "bold")).pack(pady=20)

    server_var = StringVar()
    database_var = StringVar()

    Label(connection_window, text="Servidor:", font=("Arial", 10)).pack(pady=5)
    Entry(connection_window, textvariable=server_var, width=40).pack(pady=5)

    Label(connection_window, text="Base de datos:", font=("Arial", 10)).pack(pady=5)
    Entry(connection_window, textvariable=database_var, width=40).pack(pady=5)

    Button(connection_window, text="Guardar", command=save_config).pack(pady=20)

    connection_window.mainloop()
    return config if config else None
