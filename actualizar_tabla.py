import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("sigem_ml.db")
cursor = conn.cursor()

try:
  # 1. Eliminar la tabla 'usuario' (la redundante)
  cursor.execute("DROP TABLE IF EXISTS usuario;")
  print("Tabla 'usuario' eliminada exitosamente.")

  # 2. Actualizar el rol 'oficina' a 'admin' en la tabla 'usuarios'
  cursor.execute(
      "UPDATE usuarios SET rol = 'admin' WHERE rol = 'oficina';"
  )
  print(
      "Se actualizó el rol de 'oficina' a 'admin' en la tabla 'usuarios'."
  )

  # Guardar los cambios
  conn.commit()
  print("¡Cambios aplicados correctamente!")

except Exception as e:
  print(f"Ocurrió un error: {e}")
  conn.rollback()

finally:
  conn.close()