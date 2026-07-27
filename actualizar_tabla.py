import sqlite3

conexion = sqlite3.connect('sigem_ml.db')
cursor = conexion.cursor()

# 1. Eliminamos la tabla vieja por completo
cursor.execute('DROP TABLE IF EXISTS expedientes_viejos')

# 2. La creamos de nuevo con las columnas ordenadas correctamente:
# Unnamed: 3 (Nombre), Unnamed: 4 (Año Escolar), Unnamed: 5 (Ficha)
cursor.execute('''
    CREATE TABLE expedientes_viejos (
        "Unnamed: 3" TEXT,
        "Unnamed: 4" TEXT,
        "Unnamed: 5" TEXT
    )
''')

conexion.commit()
conexion.close()

print("¡La tabla 'expedientes_viejos' ha sido eliminada y recreada exitosamente!")