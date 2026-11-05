import pandas as pd
import psycopg2

# 1. Cargar el archivo CSV desde la carpeta uploads
archivo_csv = 'uploads/public_autorizados_export_2026-08-16_161953.csv'
df = pd.read_csv(archivo_csv)

print(f"¡Cargados {len(df)} registros desde el CSV con éxito!")

# 2. Conexión directa a Supabase
URL_SUPABASE = "postgresql://postgres.cfwtrxtncgvqujimcvds:piI4T8inVAPT0n8L@aws-0-ca-central-1.pooler.supabase.com:6543/postgres"

conexion = psycopg2.connect(URL_SUPABASE, client_encoding='utf8')
cursor = conexion.cursor()

registros_migrados = 0

# Función auxiliar para manejar valores nulos de pandas
def limpiar_valor(val):
    if pd.isna(val):
        return None
    return str(val).strip()

# 3. Recorrer el DataFrame e insertar en la tabla 'autorizados' de Supabase
for index, row in df.iterrows():
    try:
        cursor.execute(
            """
            INSERT INTO autorizados (
                id_estudiante, nombres, apellidos, grado, foto_estudiante_cedula,
                padre_nombre, padre_cedula, foto_padre_cedula, padre_tel_personal, padre_tel_trabajo,
                madre_nombre, madre_cedula, foto_madre_cedula, madre_tel_personal, madre_tel_trabajo,
                tutor_nombre, tutor_cedula, foto_tutor_cedula, tutor_tel_personal, tutor_tel_trabajo,
                aut_nombre_1, aut_cedula_1, aut_parentesco_1, aut_tel_1, foto_aut_cedula_1,
                aut_nombre_2, aut_cedula_2, aut_parentesco_2, aut_tel_2, foto_aut_cedula_2,
                aut_nombre_3, aut_cedula_3, aut_parentesco_3, aut_tel_3, foto_aut_cedula_3,
                aut_nombre_4, aut_cedula_4, aut_parentesco_4, aut_tel_4, foto_aut_cedula_4,
                aut_nombre_5, aut_cedula_5, aut_parentesco_5, aut_tel_5, foto_aut_cedula_5
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            """,
            (
                limpiar_valor(row.get('id_estudiante')),
                limpiar_valor(row.get('nombres')),
                limpiar_valor(row.get('apellidos')),
                limpiar_valor(row.get('grado')),
                limpiar_valor(row.get('foto_estudiante_cedula')),
                limpiar_valor(row.get('padre_nombre')),
                limpiar_valor(row.get('padre_cedula')),
                limpiar_valor(row.get('foto_padre_cedula')),
                limpiar_valor(row.get('padre_tel_personal')),
                limpiar_valor(row.get('padre_tel_trabajo')),
                limpiar_valor(row.get('madre_nombre')),
                limpiar_valor(row.get('madre_cedula')),
                limpiar_valor(row.get('foto_madre_cedula')),
                limpiar_valor(row.get('madre_tel_personal')),
                limpiar_valor(row.get('madre_tel_trabajo')),
                limpiar_valor(row.get('tutor_nombre')),
                limpiar_valor(row.get('tutor_cedula')),
                limpiar_valor(row.get('foto_tutor_cedula')),
                limpiar_valor(row.get('tutor_tel_personal')),
                limpiar_valor(row.get('tutor_tel_trabajo')),
                limpiar_valor(row.get('aut_nombre_1')),
                limpiar_valor(row.get('aut_cedula_1')),
                limpiar_valor(row.get('aut_parentesco_1')),
                limpiar_valor(row.get('aut_tel_1')),
                limpiar_valor(row.get('foto_aut_cedula_1')),
                limpiar_valor(row.get('aut_nombre_2')),
                limpiar_valor(row.get('aut_cedula_2')),
                limpiar_valor(row.get('aut_parentesco_2')),
                limpiar_valor(row.get('aut_tel_2')),
                limpiar_valor(row.get('foto_aut_cedula_2')),
                limpiar_valor(row.get('aut_nombre_3')),
                limpiar_valor(row.get('aut_cedula_3')),
                limpiar_valor(row.get('aut_parentesco_3')),
                limpiar_valor(row.get('aut_tel_3')),
                limpiar_valor(row.get('foto_aut_cedula_3')),
                limpiar_valor(row.get('aut_nombre_4')),
                limpiar_valor(row.get('aut_cedula_4')),
                limpiar_valor(row.get('aut_parentesco_4')),
                limpiar_valor(row.get('aut_tel_4')),
                limpiar_valor(row.get('foto_aut_cedula_4')),
                limpiar_valor(row.get('aut_nombre_5')),
                limpiar_valor(row.get('aut_cedula_5')),
                limpiar_valor(row.get('aut_parentesco_5')),
                limpiar_valor(row.get('aut_tel_5')),
                limpiar_valor(row.get('foto_aut_cedula_5'))
            )
        )
        registros_migrados += 1
    except Exception as e:
        print(f"Error al insertar el registro {index}: {e}")

conexion.commit()
cursor.close()
conexion.close()

print(f"¡Migración de autorizados completada! Se registraron {registros_migrados} registros en Supabase.")