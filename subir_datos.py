import pandas as pd
from sqlalchemy import create_engine

# Tu URL de conexión de Render que acabamos de usar
DATABASE_URL = 'postgresql://sigem_db_m1ak_user:bSLhVbXQjbDafy0IlKVKCtnOdb9GdWxf@dpg-d9kb85e417fc73ehr0og-a.oregon-postgres.render.com:5432/sigem_db_m1ak'

# Conectar a la base de datos
engine = create_engine(DATABASE_URL)

# Leer tu archivo CSV con el nombre correcto y el separador adecuado
df = pd.read_csv('EXPEDIENTES.csv', sep=';')

# Subir los datos a la tabla 'expedientes_viejos' de forma automática
df.to_sql('expedientes_viejos', engine, if_exists='replace', index=False)

print('¡Datos subidos exitosamente!')