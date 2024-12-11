CREATE_RESERVACIONES_TABLE = """
CREATE TABLE IF NOT EXISTS Reservaciones (
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

CREATE_HISTORIAL_TABLE = """
CREATE TABLE IF NOT EXISTS Historial (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre_archivo VARCHAR(255),
    fecha_subida DATETIME DEFAULT GETDATE()
);
"""
