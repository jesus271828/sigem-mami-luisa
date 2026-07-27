import sqlite3
import os

def recrear_tabla():
    db_path = 'sigem_ml.db'
    
    if not os.path.exists(db_path):
        print(f"⚠️ No se encontró la base de datos '{db_path}' en esta carpeta.")
        return

    # Conectarse a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Conectado a la base de datos...")

    # 1. Eliminar la tabla existente
    cursor.execute("DROP TABLE IF EXISTS estudiantes;")
    print("🗑️ Tabla 'estudiantes' anterior eliminada.")

    # 2. Crear la nueva tabla con la estructura solicitada
    cursor.execute("""
        CREATE TABLE estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orden INTEGER,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            id_estudiante TEXT UNIQUE NOT NULL,
            foto_estudiante_cedula TEXT
        );
    """)
    print("✨ Nueva tabla 'estudiantes' creada con éxito.")

    conn.commit()
    conn.close()
    print("Base de datos guardada y cerrada correctamente.")

if __name__ == "__main__":
    recrear_tabla()