import sqlite3

def limpiar_y_reparar():
    # Conectamos a la base de datos
    conn = sqlite3.connect('sigem_ml.db')
    cursor = conn.cursor()
    
    # 1. Asegurarnos de que la tabla estudiantes tenga la columna 'grado'
    try:
        cursor.execute("ALTER TABLE estudiantes ADD COLUMN grado TEXT;")
        print("Columna 'grado' agregada exitosamente a la tabla estudiantes.")
    except sqlite3.OperationalError:
        print("La columna 'grado' ya existe en la tabla estudiantes.")
        
    # 2. Vaciar las tres tablas requeridas
    tablas = ['autorizados', 'estudiantes', 'inscripciones']
    for tabla in tablas:
        try:
            cursor.execute(f"DELETE FROM {tabla};")
            print(f"Registros de la tabla '{tabla}' eliminados correctamente.")
        except sqlite3.OperationalError as e:
            print(f"No se pudo limpiar la tabla '{tabla}' (quizás no existe aún): {e}")
            
    # Guardamos los cambios definitivamente
    conn.commit()
    conn.close()
    print("¡Base de datos limpiada y reparada con éxito!")

if __name__ == '__main__':
    limpiar_y_reparar()