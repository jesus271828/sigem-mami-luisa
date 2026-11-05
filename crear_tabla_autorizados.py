import sqlite3
import os

def recrear_tabla_autorizados():
    db_path = 'sigem_ml.db'
    
    if not os.path.exists(db_path):
        print(f"⚠️ No se encontró la base de datos '{db_path}' en esta carpeta.")
        return

    # Conectarse a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Conectado a la base de datos...")

    # 1. Eliminar la tabla 'autorizados' existente si la hay
    cursor.execute("DROP TABLE IF EXISTS autorizados;")
    print("🗑️ Tabla 'autorizados' anterior eliminada.")

    # 2. Crear la nueva tabla con la estructura solicitada
    cursor.execute("""
        CREATE TABLE autorizados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_estudiante TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            grado TEXT,
            foto_estudiante_cedula TEXT,
            
            -- Información del Padre
            padre_nombre TEXT,
            padre_cedula TEXT,
            foto_padre_cedula TEXT,
            padre_tel_personal TEXT,
            padre_tel_trabajo TEXT,
            
            -- Información de la Madre
            madre_nombre TEXT,
            madre_cedula TEXT,
            foto_madre_cedula TEXT,
            madre_tel_personal TEXT,
            madre_tel_trabajo TEXT,
            
            -- Información del Tutor
            tutor_nombre TEXT,
            tutor_cedula TEXT,
            foto_tutor_cedula TEXT,
            tutor_tel_personal TEXT,
            tutor_tel_trabajo TEXT,
            
            -- Autorizado 1
            aut_nombre_1 TEXT,
            aut_cedula_1 TEXT,
            aut_parentesco_1 TEXT,
            aut_tel_1 TEXT,
            foto_aut_cedula_1 TEXT,
            
            -- Autorizado 2
            aut_nombre_2 TEXT,
            aut_cedula_2 TEXT,
            aut_parentesco_2 TEXT,
            aut_tel_2 TEXT,
            foto_aut_cedula_2 TEXT,
            
            -- Autorizado 3
            aut_nombre_3 TEXT,
            aut_cedula_3 TEXT,
            aut_parentesco_3 TEXT,
            aut_tel_3 TEXT,
            foto_aut_cedula_3 TEXT,
            
            -- Autorizado 4
            aut_nombre_4 TEXT,
            aut_cedula_4 TEXT,
            aut_parentesco_4 TEXT,
            aut_tel_4 TEXT,
            foto_aut_cedula_4 TEXT,
            
            -- Autorizado 5
            aut_nombre_5 TEXT,
            aut_cedula_5 TEXT,
            aut_parentesco_5 TEXT,
            aut_tel_5 TEXT,
            foto_aut_cedula_5 TEXT,
            
            FOREIGN KEY (id_estudiante) REFERENCES estudiantes (id_estudiante)
        );
    """)
    print("✨ Nueva tabla 'autorizados' creada con éxito y con todos los campos hasta 5 autorizados.")

    conn.commit()
    conn.close()
    print("Base de datos guardada y cerrada correctamente.")

if __name__ == "__main__":
    recrear_tabla_autorizados()