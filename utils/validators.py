def validate_data(df):
    # Validar que las columnas requeridas estén presentes
    required_columns = ["Fecha", "Hora", "Estado"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Columna requerida faltante: {col}")
    return True
