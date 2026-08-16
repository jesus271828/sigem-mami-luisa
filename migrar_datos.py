import pandas as pd
import psycopg2

# 1. Cargar el archivo CSV de expedientes desde la carpeta uploads
df = pd.read_csv('uploads/public_expedientes_viejos_export_2026-08-16_191527.csv')

# 2. Filtrar y seleccionar únicamente las columnas útiles (índices 3, 4 y 5)
df_limpio = df.iloc[1:, [3, 4, 5]].copy()
df_limpio.columns = ['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5']

# Eliminar filas donde el nombre (Unnamed: 3) esté vacío
df_limpio = df_limpio.dropna(subset=['Unnamed: 3'])

# 3. Conexión directa a Supabase forzando la codificación UTF-8
URL_SUPABASE = "postgresql://postgres.cfwtrxtncgvqujimcvds:piI4T8inVAPT0n8L@aws-0-ca-central-1.pooler.supabase.com:6543/postgres"

conexion = psycopg2.connect(URL_SUPABASE, client_encoding='utf8')
cursor = conexion.cursor()

registros_migrados = 0

# 4. Recorrer el DataFrame e insertar directamente en Supabase
for index, row in df_limpio.iterrows():
    nombre = None if pd.isna(row['Unnamed: 3']) else str(row['Unnamed: 3']).strip()
    ano_escolar = None if pd.isna(row['Unnamed: 4']) else str(row['Unnamed: 4']).strip()
    ficha = None if pd.isna(row['Unnamed: 5']) else str(row['Unnamed: 5']).strip()
    
    try:
        cursor.execute(
            """
            INSERT INTO expedientes_viejos ("Unnamed: 3", "Unnamed: 4", "Unnamed: 5")
            VALUES (%s, %s, %s)
            """,
            (nombre, ano_escolar, ficha)
        )
        registros_migrados += 1
    except Exception as e:
        print(f"Error al insertar el registro {nombre}: {e}")

# Guardar cambios y cerrar conexión de forma segura
conexion.commit()
cursor.close()
conexion.close()

print(f"¡Migración a Supabase completada con éxito! Se registraron {registros_migrados} expedientes.")