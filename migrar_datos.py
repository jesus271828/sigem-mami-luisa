import pandas as pd
import sqlite3

# 1. Leer solo la hoja llamada 'BASE DE DATOS'
# header=4 indica que tus encabezados (NOMBRE, AÑO ESCOLAR, FICHA) están en la fila 5
df = pd.read_excel('EXPEDIENTES.xlsm', sheet_name='BASE DE DATOS', header=4, engine='openpyxl')

# 2. Conectar y guardar en la base de datos
conn = sqlite3.connect('sigem_ml.db')
df.to_sql('expedientes_viejos', conn, if_exists='replace', index=False)
conn.close()

print("¡La hoja 'BASE DE DATOS' ha sido migrada con éxito!")