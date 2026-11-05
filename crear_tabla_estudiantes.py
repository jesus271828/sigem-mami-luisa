from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurar la carpeta donde se guardarán las fotos subidas
CARPETA_UPLOADS = 'uploads'
app.config['CARPETA_UPLOADS'] = CARPETA_UPLOADS

# Asegurar que la carpeta 'uploads' exista físicamente
os.makedirs(CARPETA_UPLOADS, exist_ok=True)

# Función para inicializar la base de datos y la tabla 'estudiantes'
def inicializar_base_datos():
    conexion = sqlite3.connect('sigem_ml.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            edad INTEGER,
            sexo TEXT NOT NULL,
            nacionalidad TEXT,
            grado TEXT NOT NULL,
            seccion TEXT NOT NULL,
            direccion TEXT NOT NULL,
            nombre_tutor TEXT NOT NULL,
            parentesco_tutor TEXT,
            telefono_tutor TEXT NOT NULL,
            correo_tutor TEXT,
            alergias_condiciones TEXT,
            foto TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("¡Base de datos 'sigem_ml.db' y tabla 'estudiantes' listas!")

# Ejecutar al iniciar la aplicación
inicializar_base_datos()

@app.route('/')
def index():
    return "Sistema SIGEM Mami Luisa activo con manejo de fotos."

# Ruta para procesar el formulario, guardar la foto y registrar al estudiante
@app.route('/inscribir', methods=['POST'])
def inscribir():
    # Captura de todos los campos de texto del formulario
    matricula = request.form.get('matricula')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    edad = request.form.get('edad')
    sexo = request.form.get('sexo')
    nacionalidad = request.form.get('nacionalidad')
    grado = request.form.get('grado')
    seccion = request.form.get('seccion')
    direccion = request.form.get('direccion')
    nombre_tutor = request.form.get('nombre_tutor')
    parentesco_tutor = request.form.get('parentesco_tutor')
    telefono_tutor = request.form.get('telefono_tutor')
    correo_tutor = request.form.get('correo_tutor')
    alergias_condiciones = request.form.get('alergias_condiciones')
    
    # Procesamiento y almacenamiento seguro de la foto
    foto_file = request.files.get('foto')
    filename = "default.jpg" # Valor por si no se adjunta foto
    
    if foto_file and foto_file.filename != '':
        # Limpia el nombre del archivo para evitar caracteres extraños o maliciosos
        filename = secure_filename(foto_file.filename)
        # Guarda la foto físicamente dentro de la carpeta 'uploads'
        ruta_guardado = os.path.join(app.config['CARPETA_UPLOADS'], filename)
        foto_file.save(ruta_guardado)

    # Guardar todos los datos junto con el nombre del archivo de la foto en 'sigem_ml.db'
    conexion = sqlite3.connect('sigem_ml.db')
    cursor = conexion.cursor()

    cursor.execute('''
        INSERT INTO estudiantes (
            matricula, nombres, apellidos, fecha_nacimiento, edad, sexo, 
            nacionalidad, grado, seccion, direccion, nombre_tutor, 
            parentesco_tutor, telefono_tutor, correo_tutor, alergias_condiciones, foto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        matricula, nombres, apellidos, fecha_nacimiento, edad, sexo,
        nacionalidad, grado, seccion, direccion, nombre_tutor,
        parentesco_tutor, telefono_tutor, correo_tutor, alergias_condiciones, filename
    ))

    conexion.commit()
    conexion.close()

    return "¡Estudiante y foto registrados exitosamente en sigem_ml.db!"

if __name__ == '__main__':
    app.run(debug=True)