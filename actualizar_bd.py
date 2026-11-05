import sqlite3

def actualizar_tabla():
    try:
        conn = sqlite3.connect('sigem_ml.db')
        cursor = conn.cursor()
        
        # Intentamos agregar las columnas. 
        # Si ya existen, SQLite lanzará un error que ignoraremos.
        cursor.execute("ALTER TABLE usuarios ADD COLUMN nombre_completo TEXT")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN curso_asignado TEXT")
        
        conn.commit()
        print("¡Columnas 'nombre_completo' y 'curso_asignado' agregadas con éxito!")
    except sqlite3.OperationalError as e:
        print(f"Nota: Es posible que las columnas ya existan. Detalle: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    actualizar_tabla()