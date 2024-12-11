from database.connection import connect_to_db
from database.queries import CREATE_RESERVACIONES_TABLE, CREATE_HISTORIAL_TABLE

def setup_database(config):
    """Crea las tablas necesarias si no existen."""
    connection = connect_to_db(config)
    cursor = connection.cursor()
    try:
        cursor.execute(CREATE_RESERVACIONES_TABLE)
        cursor.execute(CREATE_HISTORIAL_TABLE)
        connection.commit()
    except Exception as e:
        print(f"Error al configurar la base de datos: {e}")
    finally:
        connection.close()
 