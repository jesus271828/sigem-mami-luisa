import sqlite3

def limpiar_tablas():
    # Conecta a tu base de datos real 'sigem_ml.db'
    conexion = sqlite3.connect('sigem_ml.db')
    cursor = conexion.cursor()
    
    try:
        # Vaciar las tablas solicitadas
        cursor.execute("DELETE FROM autorizados;")
        cursor.execute("DELETE FROM estudiantes;")
        cursor.execute("DELETE FROM inscripciones;")
        
        # Reiniciar los contadores autoincrementables (sqlite_sequence)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('autorizados', 'estudiantes', 'inscripciones');")
        
        conexion.commit()
        print("¡Las tablas autorizados, estudiantes e inscripciones han sido limpiadas exitosamente!")
    except Exception as e:
        conexion.rollback()
        print(f"Ocurrió un error al limpiar las tablas: {e}")
    finally:
        conexion.close()

if __name__ == '__main__':
    limpiar_tablas()