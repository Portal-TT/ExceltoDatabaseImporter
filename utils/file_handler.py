import pandas as pd
from tkinter import filedialog, messagebox

def load_file(tree, progress):
    """Cargar archivo Excel o CSV."""
    file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel o CSV", "*.xls *.xlsx *.csv")])
    if not file_path:
        messagebox.showinfo("Información", "No se seleccionó ningún archivo.")
        return

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')

        # Mostrar datos en la tabla
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for column in df.columns:
            tree.heading(column, text=column)
            tree.column(column, width=100)
        for row in tree.get_children():
            tree.delete(row)
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo: {e}")
