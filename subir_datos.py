import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql://sigem_db_m1ak_user:bSLhVbXQjbDafy0IlKVKCtnOdb9GdWxf"
    "@dpg-d9kb85e417fc73ehr0og-a.oregon-postgres.render.com:5432/sigem_db_m1ak"
)
engine = create_engine(DATABASE_URL)

# Lee el CSV omitiendo las primeras 6 filas vacías y tomando la fila 7 como cabecera (según se veía en tu captura)
df = pd.read_csv("EXPEDIENTES.csv", sep=";", skiprows=6)

# Limpiamos los nombres de las columnas para que no tengan espacios ni caracteres raros
df = df.dropna(
    how="all"
)  # Elimina filas totalmente vacías si las hay
# Si las columnas de tu CSV se llaman por ejemplo 'NOMBRE', 'AÑO ESCOLAR', 'FICHA', renorbrémoslas estandarizadas:
# Vamos a ver qué columnas tiene el DataFrame imprimiéndolas o asignándolas directamente:
print("Columnas detectadas:", df.columns)

# Subimos limpio a la base de datos
df.to_sql("expedientes_viejos", engine, if_exists="replace", index=True, index_label="id")
print("¡Datos limpios subidos exitosamente!")