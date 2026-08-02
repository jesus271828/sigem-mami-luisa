import sqlite3

def agregar_columna_orden():
    conexion = sqlite3.connect('sigem_ml.db')
    cursor = conexion.cursor()
    try:
        cursor.execute("ALTER TABLE estudiantes ADD COLUMN orden INTEGER DEFAULT 0;")
        conexion.commit()
        print("¡Columna 'orden' agregada exitosamente a la tabla estudiantes!")
    except Exception as e:
        print(f"La columna ya existe o hubo un error: {e}")
    finally:
        cursor.close()
        conexion.close()

if __name__ == '__main__':
    agregar_columna_orden()