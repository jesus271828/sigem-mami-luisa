import pandas as pd
from sqlalchemy import create_engine, types

csv_filename = 'public_estudiantes_export_2026-08-16_123445.csv'
df = pd.read_csv(csv_filename)

if 'id' in df.columns:
    df = df.drop(columns=['id'])

supabase_url = 'postgresql://postgres:piI4T8inVAPT0n8L@db.cfwtrxtncgvqujimcvds.supabase.co:5432/postgres'

engine = create_engine(supabase_url)

dtype_dict = {col: types.TEXT() for col in df.columns}

df.to_sql('estudiantes', engine, if_exists='append', index=False, dtype=dtype_dict)

print("¡Listo! Todos los estudiantes fueron migrados a Supabase con éxito.")