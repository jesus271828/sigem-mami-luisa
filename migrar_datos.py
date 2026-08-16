import pandas as pd
import psycopg2

# Tu cadena de conexión completa
DATABASE_URL = "postgresql://postgres.cfwtrxtncgvqujimcvds:piI4T8inVAPT0n8L@aws-0-ca-central-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Nombre del archivo CSV
csv_filename = "uploads/public_inscripciones_export_2026-08-16_142435.csv"

print(f"Leyendo el archivo {csv_filename}...")
df = pd.read_csv(csv_filename)

# Preparar datos: convertir nulos a formato compatible con SQL
df = df.where(pd.notnull(df), None)

print(f"Total de registros a migrar: {len(df)}")

try:
    print("Conectando a Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("¡Conexión exitosa!")
except Exception as e:
    print("Error al conectar:", e)
    exit()

exitosos = 0
errores = 0

# Iterar sobre las filas del CSV e insertar
for index, row in df.iterrows():
    try:
        columns = list(df.columns)
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join([f'"{col}"' for col in columns])
        
        sql = f'INSERT INTO inscripciones ({columns_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING;'
        
        values = [row[col] for col in columns]
        
        cursor.execute(sql, values)
        conn.commit()
        exitosos += 1
    except Exception as err:
        conn.rollback()
        print(f"Error en fila {index}: {err}")
        errores += 1

cursor.close()
conn.close()

print(f"\n--- Migración Finalizada ---")
print(f"Insertados: {exitosos} | Errores: {errores}")