import sqlite3

def crear_tablas():
    try:
        conexion = sqlite3.connect('sigem_ml.db')
        cursor = conexion.cursor()
        
        # Tabla dinámica para guardar CADA input del HTML (notas, asistencias, periodos, recuperaciones, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calificaciones_detalle (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante INTEGER NOT NULL,
                tipo_informe TEXT NOT NULL,
                campo_nombre TEXT NOT NULL,
                valor TEXT DEFAULT '',
                UNIQUE(id_estudiante, tipo_informe, campo_nombre),
                FOREIGN KEY (id_estudiante) 
                    REFERENCES estudiantes(id_estudiante) 
                    ON DELETE CASCADE
            );
        """)
        
        # Tabla para metadatos generales del informe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS informes_generales (
                id_informe INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante INTEGER NOT NULL,
                tipo_informe TEXT NOT NULL,
                datos_json TEXT,
                UNIQUE(id_estudiante, tipo_informe),
                FOREIGN KEY (id_estudiante) 
                    REFERENCES estudiantes(id_estudiante) 
                    ON DELETE CASCADE
            );
        """)
        
        conexion.commit()
        cursor.close()
        conexion.close()
        print("¡Tablas dinámicas listas para capturar todos los datos del HTML!")
        
    except Exception as e:
        print(f"Error al crear las tablas: {e}")

if __name__ == '__main__':
    crear_tablas()