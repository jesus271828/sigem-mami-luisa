import sqlite3

def limpiar_base_datos():
    # Conectamos a tu base de datos
    conn = sqlite3.connect('sigem_ml.db')
    cursor = conn.cursor()
    
    # Lista de tablas que queremos vaciar (dejando intacta la de expedientes)
    tablas_a_limpiar = ['asistencia', 'autorizados', 'estudiantes']
    
    try:
        for tabla in tablas_a_limpiar:
            cursor.execute(f"DELETE FROM {tabla}")
            print(f"Tabla '{tabla}' limpiada exitosamente.")
        
        conn.commit()
        print("\nLimpieza completada. Los expedientes viejos siguen intactos.")
    except Exception as e:
        print(f"Error al limpiar: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    confirmar = input("¿Estás seguro de que quieres borrar todos los estudiantes, autorizados y asistencias? (s/n): ")
    if confirmar.lower() == 's':
        limpiar_base_datos()
    else:
        print("Operación cancelada.")