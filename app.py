import os
import base64
import sqlite3
from flask import Flask, render_template, make_response, request, redirect, url_for, session, flash, send_file
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE_URL = os.environ.get('DATABASE_URL')

class PostgresCursorWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()

    def execute(self, query, params=None):
        if params:
            query = query.replace('?', '%s')
            self.cur.execute(query, params)
        else:
            self.cur.execute(query)
        return self

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def commit(self):
        return self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

def get_db_connection():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return PostgresCursorWrapper(conn)
    else:
        conn = sqlite3.connect('sigem_ml.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    if DATABASE_URL:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id SERIAL PRIMARY KEY,
                id_estudiante TEXT,
                nombres TEXT,
                apellidos TEXT,
                grado TEXT,
                foto_estudiante_cedula TEXT,
                numero_orden INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS inscripciones (
                id SERIAL PRIMARY KEY,
                anio_escolar TEXT, fecha_inscripcion TEXT, id_estudiante TEXT, nombres TEXT, apellidos TEXT,
                grado TEXT, fecha_nacimiento TEXT, edad TEXT, sexo TEXT, nacionalidad TEXT,
                lugar_nac TEXT, direccion TEXT, cant_hermanos TEXT, edades_hermanos TEXT,
                lugar_ocupa TEXT, tipo_sangre TEXT, seguro_medico TEXT, foto_estudiante_cedula TEXT,
                alergias TEXT, medicamentos TEXT, medico_pediatra TEXT, centro_medico TEXT,
                emergencia_tel TEXT, emergencia_nombre TEXT, emergencia_parentesco TEXT,
                padre_nombre TEXT, padre_sector TEXT, padre_direccion TEXT, padre_profesion TEXT,
                padre_cedula TEXT, foto_padre_cedula TEXT, padre_nivel TEXT, padre_religion TEXT, 
                padre_tel_personal TEXT, padre_tel_trabajo TEXT, padre_correo TEXT,
                madre_nombre TEXT, madre_sector TEXT, madre_direccion TEXT, madre_profesion TEXT,
                madre_cedula TEXT, foto_madre_cedula TEXT, madre_nivel TEXT, madre_religion TEXT, 
                madre_tel_personal TEXT, madre_tel_trabajo TEXT, madre_correo TEXT,
                tutor_nombre TEXT, tutor_sector TEXT, tutor_direccion TEXT, tutor_profesion TEXT,
                tutor_cedula TEXT, foto_tutor_cedula TEXT, tutor_nivel TEXT, tutor_religion TEXT, 
                tutor_tel_personal TEXT, tutor_tel_trabajo TEXT, tutor_correo TEXT,
                vive_nombres TEXT, vive_parentesco TEXT, vive_cedula TEXT, foto_vive_cedula TEXT, 
                vive_direccion TEXT, vive_sector TEXT, vive_profesion TEXT, vive_nivel TEXT, 
                vive_religion TEXT, vive_tel_personal TEXT, vive_tel_trabajo TEXT, vive_correo TEXT,
                econ_nombres TEXT, econ_parentesco TEXT, econ_cedula TEXT, foto_econ_cedula TEXT, 
                econ_direccion TEXT, econ_sector TEXT, econ_profesion TEXT, econ_lugar_trabajo TEXT, 
                econ_tel_personal TEXT, econ_tel_trabajo TEXT, econ_correo TEXT,
                aut_nombre_1 TEXT, aut_cedula_1 TEXT, aut_parentesco_1 TEXT, aut_tel_1 TEXT, foto_aut_cedula_1 TEXT,
                aut_nombre_2 TEXT, aut_cedula_2 TEXT, aut_parentesco_2 TEXT, aut_tel_2 TEXT, foto_aut_cedula_2 TEXT,
                aut_nombre_3 TEXT, aut_cedula_3 TEXT, aut_parentesco_3 TEXT, aut_tel_3 TEXT, foto_aut_cedula_3 TEXT,
                aut_nombre_4 TEXT, aut_cedula_4 TEXT, aut_parentesco_4 TEXT, aut_tel_4 TEXT, foto_aut_cedula_4 TEXT,
                aut_nombre_5 TEXT, aut_cedula_5 TEXT, aut_parentesco_5 TEXT, aut_tel_5 TEXT, foto_aut_cedula_5 TEXT,
                autoriza_medicamentos TEXT, autoriza_redes TEXT, firma_redes TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS autorizados (
                id SERIAL PRIMARY KEY,
                id_estudiante TEXT, nombres TEXT, apellidos TEXT, grado TEXT, foto_estudiante_cedula TEXT,
                padre_nombre TEXT, padre_cedula TEXT, foto_padre_cedula TEXT, padre_tel_personal TEXT, padre_tel_trabajo TEXT,
                madre_nombre TEXT, madre_cedula TEXT, foto_madre_cedula TEXT, madre_tel_personal TEXT, madre_tel_trabajo TEXT,
                tutor_nombre TEXT, tutor_cedula TEXT, foto_tutor_cedula TEXT, tutor_tel_personal TEXT, tutor_tel_trabajo TEXT,
                aut_nombre_1 TEXT, aut_cedula_1 TEXT, aut_parentesco_1 TEXT, aut_tel_1 TEXT, foto_aut_cedula_1 TEXT,
                aut_nombre_2 TEXT, aut_cedula_2 TEXT, aut_parentesco_2 TEXT, aut_tel_2 TEXT, foto_aut_cedula_2 TEXT,
                aut_nombre_3 TEXT, aut_cedula_3 TEXT, aut_parentesco_3 TEXT, aut_tel_3 TEXT, foto_aut_cedula_3 TEXT,
                aut_nombre_4 TEXT, aut_cedula_4 TEXT, aut_parentesco_4 TEXT, aut_tel_4 TEXT, foto_aut_cedula_4 TEXT,
                aut_nombre_5 TEXT, aut_cedula_5 TEXT, aut_parentesco_5 TEXT, aut_tel_5 TEXT, foto_aut_cedula_5 TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre_completo TEXT,
                username TEXT,
                password TEXT,
                rol TEXT,
                curso_asignado TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expedientes_viejos (
                id SERIAL PRIMARY KEY,
                "Unnamed: 3" TEXT,
                "Unnamed: 4" TEXT,
                "Unnamed: 5" TEXT
            )
        ''')
    else:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante TEXT, nombres TEXT, apellidos TEXT, grado TEXT,
                foto_estudiante_cedula TEXT, numero_orden INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anio_escolar TEXT, fecha_inscripcion TEXT, id_estudiante TEXT, nombres TEXT, apellidos TEXT,
                grado TEXT, fecha_nacimiento TEXT, edad TEXT, sexo TEXT, nacionalidad TEXT,
                lugar_nac TEXT, direccion TEXT, cant_hermanos TEXT, edades_hermanos TEXT,
                lugar_ocupa TEXT, tipo_sangre TEXT, seguro_medico TEXT, foto_estudiante_cedula TEXT,
                alergias TEXT, medicamentos TEXT, medico_pediatra TEXT, centro_medico TEXT,
                emergencia_tel TEXT, emergencia_nombre TEXT, emergencia_parentesco TEXT,
                padre_nombre TEXT, padre_sector TEXT, padre_direccion TEXT, padre_profesion TEXT,
                padre_cedula TEXT, foto_padre_cedula TEXT, padre_nivel TEXT, padre_religion TEXT, 
                padre_tel_personal TEXT, padre_tel_trabajo TEXT, padre_correo TEXT,
                madre_nombre TEXT, madre_sector TEXT, madre_direccion TEXT, madre_profesion TEXT,
                madre_cedula TEXT, foto_madre_cedula TEXT, madre_nivel TEXT, madre_religion TEXT, 
                madre_tel_personal TEXT, madre_tel_trabajo TEXT, madre_correo TEXT,
                tutor_nombre TEXT, tutor_sector TEXT, tutor_direccion TEXT, tutor_profesion TEXT,
                tutor_cedula TEXT, foto_tutor_cedula TEXT, tutor_nivel TEXT, tutor_religion TEXT, 
                tutor_tel_personal TEXT, tutor_tel_trabajo TEXT, tutor_correo TEXT,
                vive_nombres TEXT, vive_parentesco TEXT, vive_cedula TEXT, foto_vive_cedula TEXT, 
                vive_direccion TEXT, vive_sector TEXT, vive_profesion TEXT, vive_nivel TEXT, 
                vive_religion TEXT, vive_tel_personal TEXT, vive_tel_trabajo TEXT, vive_correo TEXT,
                econ_nombres TEXT, econ_parentesco TEXT, econ_cedula TEXT, foto_econ_cedula TEXT, 
                econ_direccion TEXT, econ_sector TEXT, econ_profesion TEXT, econ_lugar_trabajo TEXT, 
                econ_tel_personal TEXT, econ_tel_trabajo TEXT, econ_correo TEXT,
                aut_nombre_1 TEXT, aut_cedula_1 TEXT, aut_parentesco_1 TEXT, aut_tel_1 TEXT, foto_aut_cedula_1 TEXT,
                aut_nombre_2 TEXT, aut_cedula_2 TEXT, aut_parentesco_2 TEXT, aut_tel_2 TEXT, foto_aut_cedula_2 TEXT,
                aut_nombre_3 TEXT, aut_cedula_3 TEXT, aut_parentesco_3 TEXT, aut_tel_3 TEXT, foto_aut_cedula_3 TEXT,
                aut_nombre_4 TEXT, aut_cedula_4 TEXT, aut_parentesco_4 TEXT, aut_tel_4 TEXT, foto_aut_cedula_4 TEXT,
                aut_nombre_5 TEXT, aut_cedula_5 TEXT, aut_parentesco_5 TEXT, aut_tel_5 TEXT, foto_aut_cedula_5 TEXT,
                autoriza_medicamentos TEXT, autoriza_redes TEXT, firma_redes TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autorizados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante TEXT, nombres TEXT, apellidos TEXT, grado TEXT, foto_estudiante_cedula TEXT,
                padre_nombre TEXT, padre_cedula TEXT, foto_padre_cedula TEXT, padre_tel_personal TEXT, padre_tel_trabajo TEXT,
                madre_nombre TEXT, madre_cedula TEXT, foto_madre_cedula TEXT, madre_tel_personal TEXT, madre_tel_trabajo TEXT,
                tutor_nombre TEXT, tutor_cedula TEXT, foto_tutor_cedula TEXT, tutor_tel_personal TEXT, tutor_tel_trabajo TEXT,
                aut_nombre_1 TEXT, aut_cedula_1 TEXT, aut_parentesco_1 TEXT, aut_tel_1 TEXT, foto_aut_cedula_1 TEXT,
                aut_nombre_2 TEXT, aut_cedula_2 TEXT, aut_parentesco_2 TEXT, aut_tel_2 TEXT, foto_aut_cedula_2 TEXT,
                aut_nombre_3 TEXT, aut_cedula_3 TEXT, aut_parentesco_3 TEXT, aut_tel_3 TEXT, foto_aut_cedula_3 TEXT,
                aut_nombre_4 TEXT, aut_cedula_4 TEXT, aut_parentesco_4 TEXT, aut_tel_4 TEXT, foto_aut_cedula_4 TEXT,
                aut_nombre_5 TEXT, aut_cedula_5 TEXT, aut_parentesco_5 TEXT, aut_tel_5 TEXT, foto_aut_cedula_5 TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT, username TEXT, password TEXT, rol TEXT, curso_asignado TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expedientes_viejos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Unnamed: 3" TEXT, "Unnamed: 4" TEXT, "Unnamed: 5" TEXT
            )
        ''')
    conn.commit()
    conn.close()

# Forzar la creación de tablas al iniciar (tanto en local como en Gunicorn/Render)
init_db()

# --- RUTA PRINCIPAL (INDEX Y MENU) ---
@app.route('/')
@app.route('/menu')
def index():
    usuario_actual = session.get('usuario')
    if not usuario_actual:
        flash('Por favor inicie sesión.', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    try:
        total_inscripciones = conn.execute('SELECT COUNT(*) FROM inscripciones').fetchone()[0]
    except:
        total_inscripciones = 0
    try:
        total_estudiantes = conn.execute('SELECT COUNT(*) FROM estudiantes').fetchone()[0]
    except:
        total_estudiantes = 0
    try:
        total_expedientes = conn.execute('SELECT COUNT(*) FROM expedientes_viejos').fetchone()[0]
    except:
        total_expedientes = 0
    try:
        total_usuarios = conn.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
    except:
        total_usuarios = 0
    conn.close()
    
    return render_template('menu.html', 
                           total_inscripciones=total_inscripciones, 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios, 
                           usuario_actual=usuario_actual)


# --- AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_ingresado = request.form.get('usuario') or request.form.get('username')
        password = request.form.get('password') or request.form.get('contrasena')
        
        conn = get_db_connection()
        user = None
        try:
            # Como tu PostgresCursorWrapper acepta '?' y los convierte, puedes usar la misma sintaxis para ambos
            cursor = conn
            cursor.execute('SELECT username, rol, nombre_completo, curso_asignado FROM usuarios WHERE username = ? AND password = ?', (usuario_ingresado, password))
            row = cursor.fetchone()
            
            if row:
                # Dependiendo de si devolvió tupla o diccionario, lo adaptamos de forma segura:
                if isinstance(row, dict):
                    user = row
                else:
                    user = {
                        'username': row[0],
                        'rol': row[1],
                        'nombre_completo': row[2],
                        'curso_asignado': row[3] if row[3] else ''
                    }
            cursor.close()
        except Exception as e:
            print("Error general en login:", e)
            user = None
        
        if user:
            session['usuario'] = user.get('username', '')
            session['rol'] = user.get('rol', '')
            session['nombre_completo'] = user.get('nombre_completo', '')
            session['curso_asignado'] = user.get('curso_asignado', '')
            return redirect(url_for('index'))
        else:
            return "Usuario o contraseña incorrectos"
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- INSCRIPCIÓN ---
@app.route('/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if request.method == 'POST':
        def guardar_archivo(input_name):
            file = request.files.get(input_name)
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                return filepath
            return None

        anio_escolar = request.form.get('anio_escolar')
        fecha_inscripcion = request.form.get('fecha_inscripcion')
        id_estudiante = request.form.get('id_estudiante')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        grado = request.form.get('grado')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        nacionalidad = request.form.get('nacionalidad')
        lugar_nac = request.form.get('lugar_nac')
        direccion = request.form.get('direccion')
        cant_hermanos = request.form.get('cant_hermanos')
        edades_hermanos = request.form.get('edades_hermanos')
        lugar_ocupa = request.form.get('lugar_ocupa')
        tipo_sangre = request.form.get('tipo_sangre')
        seguro_medico = request.form.get('seguro_medico')
        foto_estudiante_cedula = guardar_archivo('foto_estudiante_cedula')
        alergias = request.form.get('alergias')
        medicamentos = request.form.get('medicamentos')
        medico_pediatra = request.form.get('medico_pediatra')
        centro_medico = request.form.get('centro_medico')
        emergencia_tel = request.form.get('emergencia_tel')
        emergencia_nombre = request.form.get('emergencia_nombre')
        emergencia_parentesco = request.form.get('emergencia_parentesco')

        padre_nombre = request.form.get('padre_nombre')
        padre_sector = request.form.get('padre_sector')
        padre_direccion = request.form.get('padre_direccion')
        padre_profesion = request.form.get('padre_profesion')
        padre_cedula = request.form.get('padre_cedula')
        foto_padre_cedula = guardar_archivo('foto_padre_cedula')
        padre_nivel = request.form.get('padre_nivel')
        padre_religion = request.form.get('padre_religion')
        padre_tel_personal = request.form.get('padre_tel_personal')
        padre_tel_trabajo = request.form.get('padre_tel_trabajo')
        padre_correo = request.form.get('padre_correo')

        madre_nombre = request.form.get('madre_nombre')
        madre_sector = request.form.get('madre_sector')
        madre_direccion = request.form.get('madre_direccion')
        madre_profesion = request.form.get('madre_profesion')
        madre_cedula = request.form.get('madre_cedula')
        foto_madre_cedula = guardar_archivo('foto_madre_cedula')
        madre_nivel = request.form.get('madre_nivel')
        madre_religion = request.form.get('madre_religion')
        madre_tel_personal = request.form.get('madre_tel_personal')
        madre_tel_trabajo = request.form.get('madre_tel_trabajo')
        madre_correo = request.form.get('madre_correo')

        tutor_nombre = request.form.get('tutor_nombre')
        tutor_sector = request.form.get('tutor_sector')
        tutor_direccion = request.form.get('tutor_direccion')
        tutor_profesion = request.form.get('tutor_profesion')
        tutor_cedula = request.form.get('tutor_cedula')
        foto_tutor_cedula = guardar_archivo('foto_tutor_cedula')
        tutor_nivel = request.form.get('tutor_nivel')
        tutor_religion = request.form.get('tutor_religion')
        tutor_tel_personal = request.form.get('tutor_tel_personal')
        tutor_tel_trabajo = request.form.get('tutor_tel_trabajo')
        tutor_correo = request.form.get('tutor_correo')

        vive_nombres = request.form.get('vive_nombres')
        vive_parentesco = request.form.get('vive_parentesco')
        vive_cedula = request.form.get('vive_cedula')
        foto_vive_cedula = guardar_archivo('foto_vive_cedula')
        vive_direccion = request.form.get('vive_direccion')
        vive_sector = request.form.get('vive_sector')
        vive_profesion = request.form.get('vive_profesion')
        vive_nivel = request.form.get('vive_nivel')
        vive_religion = request.form.get('vive_religion')
        vive_tel_personal = request.form.get('vive_tel_personal')
        vive_tel_trabajo = request.form.get('vive_tel_trabajo')
        vive_correo = request.form.get('vive_correo')

        econ_nombres = request.form.get('econ_nombres')
        econ_parentesco = request.form.get('econ_parentesco')
        econ_cedula = request.form.get('econ_cedula')
        foto_econ_cedula = guardar_archivo('foto_econ_cedula')
        econ_direccion = request.form.get('econ_direccion')
        econ_sector = request.form.get('econ_sector')
        econ_profesion = request.form.get('econ_profesion')
        econ_lugar_trabajo = request.form.get('econ_lugar_trabajo')
        econ_tel_personal = request.form.get('econ_tel_personal')
        econ_tel_trabajo = request.form.get('econ_tel_trabajo')
        econ_correo = request.form.get('econ_correo')

        aut_data = {}
        for i in range(1, 6):
            aut_data[f'aut_nombre_{i}'] = request.form.get(f'aut_nombre_{i}')
            aut_data[f'aut_cedula_{i}'] = request.form.get(f'aut_cedula_{i}')
            aut_data[f'aut_parentesco_{i}'] = request.form.get(f'aut_parentesco_{i}')
            aut_data[f'aut_tel_{i}'] = request.form.get(f'aut_tel_{i}')
            aut_data[f'foto_aut_cedula_{i}'] = guardar_archivo(f'foto_aut_cedula_{i}')

        autoriza_medicamentos = request.form.get('autoriza_medicamentos', 'NO')
        autoriza_redes = request.form.get('autoriza_redes', 'NO')
        firma_redes = request.form.get('firma_redes')

        try:
            conexion = get_db_connection()
            
            conexion.execute('''
                INSERT INTO estudiantes (nombres, apellidos, id_estudiante, grado, foto_estudiante_cedula)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombres, apellidos, id_estudiante, grado, foto_estudiante_cedula))
            
            conexion.execute("SELECT id FROM estudiantes ORDER BY nombres ASC, apellidos ASC")
            registros_estudiantes = conexion.fetchall()
            for indice, reg in enumerate(registros_estudiantes, start=1):
                reg_id = reg['id'] if isinstance(reg, sqlite3.Row) or hasattr(reg, 'keys') else reg[0]
                conexion.execute("UPDATE estudiantes SET numero_orden = ? WHERE id = ?", (indice, reg_id))

            conexion.execute('''
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
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                )
            ''', (
                id_estudiante, nombres, apellidos, grado, foto_estudiante_cedula,
                padre_nombre, padre_cedula, foto_padre_cedula, padre_tel_personal, padre_tel_trabajo,
                madre_nombre, madre_cedula, foto_madre_cedula, madre_tel_personal, madre_tel_trabajo,
                tutor_nombre, tutor_cedula, foto_tutor_cedula, tutor_tel_personal, tutor_tel_trabajo,
                aut_data['aut_nombre_1'], aut_data['aut_cedula_1'], aut_data['aut_parentesco_1'], aut_data['aut_tel_1'], aut_data['foto_aut_cedula_1'],
                aut_data['aut_nombre_2'], aut_data['aut_cedula_2'], aut_data['aut_parentesco_2'], aut_data['aut_tel_2'], aut_data['foto_aut_cedula_2'],
                aut_data['aut_nombre_3'], aut_data['aut_cedula_3'], aut_data['aut_parentesco_3'], aut_data['aut_tel_3'], aut_data['foto_aut_cedula_3'],
                aut_data['aut_nombre_4'], aut_data['aut_cedula_4'], aut_data['aut_parentesco_4'], aut_data['aut_tel_4'], aut_data['foto_aut_cedula_4'],
                aut_data['aut_nombre_5'], aut_data['aut_cedula_5'], aut_data['aut_parentesco_5'], aut_data['aut_tel_5'], aut_data['foto_aut_cedula_5']
            ))

            conexion.execute('''
                INSERT INTO inscripciones (
                    anio_escolar, fecha_inscripcion, id_estudiante, nombres, apellidos, grado, 
                    fecha_nacimiento, edad, sexo, nacionalidad, lugar_nac, direccion, cant_hermanos, 
                    edades_hermanos, lugar_ocupa, tipo_sangre, seguro_medico, foto_estudiante_cedula, 
                    alergias, medicamentos, medico_pediatra, centro_medico, emergencia_tel, 
                    emergencia_nombre, emergencia_parentesco,
                    padre_nombre, padre_sector, padre_direccion, padre_profesion, padre_cedula, 
                    foto_padre_cedula, padre_nivel, padre_religion, padre_tel_personal, padre_tel_trabajo, padre_correo,
                    madre_nombre, madre_sector, madre_direccion, madre_profesion, madre_cedula, 
                    foto_madre_cedula, madre_nivel, madre_religion, madre_tel_personal, madre_tel_trabajo, madre_correo,
                    tutor_nombre, tutor_sector, tutor_direccion, tutor_profesion, tutor_cedula, 
                    foto_tutor_cedula, tutor_nivel, tutor_religion, tutor_tel_personal, tutor_tel_trabajo, tutor_correo,
                    vive_nombres, vive_parentesco, vive_cedula, foto_vive_cedula, vive_direccion, 
                    vive_sector, vive_profesion, vive_nivel, vive_religion, vive_tel_personal, vive_tel_trabajo, vive_correo,
                    econ_nombres, econ_parentesco, econ_cedula, foto_econ_cedula, econ_direccion, 
                    econ_sector, econ_profesion, econ_lugar_trabajo, econ_tel_personal, econ_tel_trabajo, econ_correo,
                    aut_nombre_1, aut_cedula_1, aut_parentesco_1, aut_tel_1, foto_aut_cedula_1,
                    aut_nombre_2, aut_cedula_2, aut_parentesco_2, aut_tel_2, foto_aut_cedula_2,
                    aut_nombre_3, aut_cedula_3, aut_parentesco_3, aut_tel_3, foto_aut_cedula_3,
                    aut_nombre_4, aut_cedula_4, aut_parentesco_4, aut_tel_4, foto_aut_cedula_4,
                    aut_nombre_5, aut_cedula_5, aut_parentesco_5, aut_tel_5, foto_aut_cedula_5,
                    autoriza_medicamentos, autoriza_redes, firma_redes
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
            ''', (
                anio_escolar, fecha_inscripcion, id_estudiante, nombres, apellidos, grado, 
                fecha_nacimiento, edad, sexo, nacionalidad, lugar_nac, direccion, cant_hermanos, 
                edades_hermanos, lugar_ocupa, tipo_sangre, seguro_medico, foto_estudiante_cedula, 
                alergias, medicamentos, medico_pediatra, centro_medico, emergencia_tel, 
                emergencia_nombre, emergencia_parentesco,
                padre_nombre, padre_sector, padre_direccion, padre_profesion, padre_cedula, 
                foto_padre_cedula, padre_nivel, padre_religion, padre_tel_personal, padre_tel_trabajo, padre_correo,
                madre_nombre, madre_sector, madre_direccion, madre_profesion, madre_cedula, 
                foto_madre_cedula, madre_nivel, madre_religion, madre_tel_personal, madre_tel_trabajo, madre_correo,
                tutor_nombre, tutor_sector, tutor_direccion, tutor_profesion, tutor_cedula, 
                foto_tutor_cedula, tutor_nivel, tutor_religion, tutor_tel_personal, tutor_tel_trabajo, tutor_correo,
                vive_nombres, vive_parentesco, vive_cedula, foto_vive_cedula, vive_direccion, 
                vive_sector, vive_profesion, vive_nivel, vive_religion, vive_tel_personal, vive_tel_trabajo, vive_correo,
                econ_nombres, econ_parentesco, econ_cedula, foto_econ_cedula, econ_direccion, 
                econ_sector, econ_profesion, econ_lugar_trabajo, econ_tel_personal, econ_tel_trabajo, econ_correo,
                aut_data['aut_nombre_1'], aut_data['aut_cedula_1'], aut_data['aut_parentesco_1'], aut_data['aut_tel_1'], aut_data['foto_aut_cedula_1'],
                aut_data['aut_nombre_2'], aut_data['aut_cedula_2'], aut_data['aut_parentesco_2'], aut_data['aut_tel_2'], aut_data['foto_aut_cedula_2'],
                aut_data['aut_nombre_3'], aut_data['aut_cedula_3'], aut_data['aut_parentesco_3'], aut_data['aut_tel_3'], aut_data['foto_aut_cedula_3'],
                aut_data['aut_nombre_4'], aut_data['aut_cedula_4'], aut_data['aut_parentesco_4'], aut_data['aut_tel_4'], aut_data['foto_aut_cedula_4'],
                aut_data['aut_nombre_5'], aut_data['aut_cedula_5'], aut_data['aut_parentesco_5'], aut_data['aut_tel_5'], aut_data['foto_aut_cedula_5'],
                autoriza_medicamentos, autoriza_redes, firma_redes
            ))
            
            conexion.commit()
            conexion.close()
            flash('¡Estudiante inscrito y guardado correctamente en todas las tablas!', 'success')
        except Exception as e:
            print(f"Error al guardar en la base de datos: {e}")
            flash('Hubo un error al guardar los datos.', 'danger')

        return redirect(url_for('inscripcion'))

    return render_template('inscripcion.html', total_estudiantes=0, total_expedientes=0, total_usuarios=0)

# --- BÚSQUEDA Y OTROS MÓDULOS ---
@app.route('/menu_buscar')
def menu_buscar():
    if session.get('rol') != 'admin':
        flash('Acceso denegado.')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    try:
        total_estudiantes = conn.execute('SELECT COUNT(*) FROM inscripciones').fetchone()[0]
    except:
        total_estudiantes = 0
    try:
        total_expedientes = conn.execute('SELECT COUNT(*) FROM expedientes_viejos').fetchone()[0]
    except:
        total_expedientes = 0
    try:
        total_usuarios = conn.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
    except:
        total_usuarios = 0
    conn.close()
    
    return render_template('menu_buscar.html', 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios)

@app.route('/buscar_autorizado', methods=['GET', 'POST'])
def buscar_autorizado():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    try:
        total_estudiantes = conn.execute("SELECT COUNT(*) FROM estudiantes").fetchone()[0]
    except:
        total_estudiantes = 0
    try:
        total_expedientes = conn.execute("SELECT COUNT(*) FROM expedientes_viejos").fetchone()[0]
    except:
        total_expedientes = 0
    try:
        total_usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    except:
        total_usuarios = 0

    lista_autorizados = []

    if request.method == 'POST':
        criterio = request.form.get('criterio', '').strip()
        busqueda = f"%{criterio}%"
        
        query = """
            SELECT a.*, e.nombres as est_nombres, e.apellidos as est_apellidos, e.grado, e.foto_estudiante_cedula
            FROM autorizados a
            LEFT JOIN estudiantes e ON a.id_estudiante = e.id_estudiante
            WHERE a.aut_nombre_1 LIKE ? OR a.aut_cedula_1 LIKE ? 
               OR a.aut_nombre_2 LIKE ? OR a.aut_cedula_2 LIKE ?
               OR a.aut_nombre_3 LIKE ? OR a.aut_cedula_3 LIKE ?
               OR a.aut_nombre_4 LIKE ? OR a.aut_cedula_4 LIKE ?
               OR a.aut_nombre_5 LIKE ? OR a.aut_cedula_5 LIKE ?
        """
        rows = conn.execute(query, (busqueda, busqueda, busqueda, busqueda, busqueda, busqueda, busqueda, busqueda, busqueda, busqueda)).fetchall()
        
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')

        for row in rows:
            base_dict = dict(row)
            
            for i in range(1, 6):
                nom_campo = f'aut_nombre_{i}'
                ced_campo = f'aut_cedula_{i}'
                foto_campo = f'foto_aut_cedula_{i}'
                
                val_nom = str(base_dict.get(nom_campo, '')).lower()
                val_ced = str(base_dict.get(ced_campo, ''))
                
                if criterio.lower() in val_nom or (criterio != '' and criterio in val_ced):
                    autorizado = base_dict.copy()
                    autorizado['nombre_completo'] = base_dict.get(nom_campo, '')
                    autorizado['cedula'] = base_dict.get(ced_campo, '')
                    
                    ruta_aut = str(base_dict.get(foto_campo, '')).strip()
                    nombre_aut = ""
                    if ruta_aut:
                        nombre_aut = ruta_aut.replace('\\', '/').split('/')[-1].strip()
                        if 'uploads' in nombre_aut.lower():
                            nombre_aut = nombre_aut.split('uploads')[-1].lstrip('/\\')
                    
                    if nombre_aut and os.path.exists(os.path.join(uploads_dir, nombre_aut)):
                        autorizado['foto_autorizado'] = nombre_aut
                    else:
                        autorizado['foto_autorizado'] = ''

                    ruta_est = str(base_dict.get('foto_estudiante_cedula', '')).strip()
                    nombre_est = ""
                    if ruta_est:
                        nombre_est = ruta_est.replace('\\', '/').split('/')[-1].strip()
                        if 'uploads' in nombre_est.lower():
                            nombre_est = nombre_est.split('uploads')[-1].lstrip('/\\')
                        
                    if nombre_est and os.path.exists(os.path.join(uploads_dir, nombre_est)):
                        autorizado['foto_estudiante'] = nombre_est
                    else:
                        autorizado['foto_estudiante'] = ''

                    autorizado['nombres'] = base_dict.get('est_nombres', '')
                    autorizado['apellidos'] = base_dict.get('est_apellidos', '')

                    if autorizado not in lista_autorizados:
                        lista_autorizados.append(autorizado)

    conn.close()

    return render_template('buscar_autorizado.html',
                           autorizados=lista_autorizados,
                           total_estudiantes=total_estudiantes,
                           total_expedientes=total_expedientes,
                           total_usuarios=total_usuarios)


@app.route('/listado-estudiantes')
def listado_estudiantes():
    if 'usuario' not in session:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
        
    usuario_actual = session.get('usuario')
    rol_actual = session.get('rol')
    
    conn = get_db_connection()
    
    # Si es oficina o admin, ve todo. Si es maestro, filtra por su nombre o usuario asociado.
    if rol_actual in ['oficina', 'admin']:
        estudiantes = conn.execute('SELECT * FROM inscripciones').fetchall()
    else:
        # Ajusta 'maestro' o la columna correspondiente si en tu tabla se llama distinto (ej. profesor, usuario_id, etc.)
        estudiantes = conn.execute('SELECT * FROM inscripciones WHERE maestro = ?', (usuario_actual,)).fetchall()
        
    conn.close()
    
    return render_template('listado_estudiantes.html', estudiantes=estudiantes)


@app.route('/buscar_estudiante', methods=['GET', 'POST'])
def buscar_estudiante():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # Contadores seguros
    try:
        total_estudiantes = conn.execute("SELECT COUNT(*) FROM inscripciones").fetchone()[0]
    except:
        total_estudiantes = 0
    try:
        total_expedientes = conn.execute("SELECT COUNT(*) FROM expedientes_viejos").fetchone()[0]
    except:
        total_expedientes = 0
    try:
        total_usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    except:
        total_usuarios = 0

    # Obtener grados disponibles
    grados_disponibles = []
    try:
        grados_rows = conn.execute("SELECT DISTINCT grado FROM inscripciones WHERE grado IS NOT NULL AND grado != ''").fetchall()
        grados_disponibles = [row[0] for row in grados_rows if row[0]]
    except:
        try:
            grados_rows = conn.execute("SELECT DISTINCT curso FROM inscripciones WHERE curso IS NOT NULL AND curso != ''").fetchall()
            grados_disponibles = [row[0] for row in grados_rows if row[0]]
        except:
            pass

    # Búsqueda y filtrado
    try:
        if request.method == 'POST':
            criterio = request.form.get('criterio', '').strip()
            grado_filtro = request.form.get('grado_filtro', '').strip()
            
            query = "SELECT * FROM inscripciones WHERE 1=1"
            params = []
            
            if criterio:
                # Comprobamos campos comunes de texto
                query += " AND (nombres LIKE ? OR apellidos LIKE ?)"
                params.extend([f"%{criterio}%", f"%{criterio}%"])
                
            if grado_filtro:
                query += " AND (grado = ? OR curso = ?)"
                params.extend([grado_filtro, grado_filtro])
                
            estudiantes = conn.execute(query, params).fetchall()
        else:
            estudiantes = conn.execute("SELECT * FROM inscripciones").fetchall()
    except Exception as e:
        estudiantes = []
        
    conn.close()

    return render_template('buscar_estudiante.html',
                           estudiantes=estudiantes,
                           grados_disponibles=grados_disponibles,
                           total_estudiantes=total_estudiantes,
                           total_expedientes=total_expedientes,
                           total_usuarios=total_usuarios)


@app.route('/generar_pdf/<id_estudiante>')
def generar_pdf(id_estudiante):
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    conexion = get_db_connection()
    
    estudiante = None
    # Intentar buscar por diferentes nombres de columna de ID posibles
    for columna_id in ['id', 'id_estudiante']:
        try:
            estudiante = conexion.execute(f"SELECT * FROM inscripciones WHERE {columna_id} = ?", (id_estudiante,)).fetchone()
            if estudiante:
                break
        except:
            continue

    autorizados = None
    for columna_id in ['id_estudiante', 'id']:
        try:
            autorizados = conexion.execute(f"SELECT * FROM autorizados WHERE {columna_id} = ?", (id_estudiante,)).fetchone()
            if autorizados:
                break
        except:
            continue
        
    conexion.close()
    
    if not estudiante:
        return f"No se encontró ninguna inscripción para el estudiante con ID: {id_estudiante}", 404

    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo2.png')
    logo_src = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        logo_src = f"data:image/png;base64,{logo_base64}"
    
    html = render_template('pdf_ficha.html', estudiante=estudiante, autorizados=autorizados, logo_src=logo_src)
    
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ficha_inscripcion_{id_estudiante}.pdf'
    
    pisa_status = pisa.CreatePDF(html, dest=response.stream)
    
    if pisa_status.err:
        return 'Hubo un error al generar el PDF', 500
        
    return response

@app.route('/asistencia')
def asistencia():
    if 'rol' not in session or session['rol'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('index'))
    return render_template('asistencia.html')

@app.route('/menu_notas')
def menu_notas():
    return render_template('menu_notas.html')

@app.route('/notas1')
def notas1():
    rol = str(session.get('rol', '')).strip().lower()
    curso = str(session.get('curso_asignado', '')).strip().lower()
    if rol in ['admin', 'oficina'] or curso.startswith('1') or curso.startswith('2') or curso.startswith('3'):
        return render_template('notas1.html', estudiante=None)
    flash('Acceso denegado.', 'danger')
    return redirect(url_for('menu_notas'))

@app.route('/notas2')
def notas2():
    rol = str(session.get('rol', '')).strip().lower()
    curso = str(session.get('curso_asignado', '')).strip().lower()
    if rol in ['admin', 'oficina'] or curso.startswith('4') or curso.startswith('5') or curso.startswith('6'):
        return render_template('notas2.html', estudiante=None)
    flash('Acceso denegado.', 'danger')
    return redirect(url_for('menu_notas'))

@app.route('/planificacion')
def planificacion():
    usuario_actual = {'nombre': session.get('usuario_nombre', 'Jesus Maria Alfonseca Duverge'), 'rol': session.get('rol', 'maestro')}
    return render_template('planificacion.html', usuario=usuario_actual)



@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if session.get('rol') not in ['oficina', 'admin']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('menu'))
        
    conn = get_db_connection()
    edit_id = request.args.get('edit_id')
    maestro_a_editar = conn.execute("SELECT * FROM usuarios WHERE id = ?", (edit_id,)).fetchone() if edit_id else None

    if request.method == 'POST':
        nombre_completo = request.form['nombre_completo']
        username = request.form['nombre_usuario']
        password = request.form['contrasena']
        rol = request.form['rol']
        curso_asignado = request.form['curso_asignado']
        id_usuario = request.form.get('id_usuario')

        if id_usuario:
            conn.execute("UPDATE usuarios SET nombre_completo = ?, username = ?, password = ?, rol = ?, curso_asignado = ? WHERE id = ?",
                         (nombre_completo, username, password, rol, curso_asignado, id_usuario))
            flash('Maestro actualizado.', 'success')
        else:
            conn.execute("INSERT INTO usuarios (nombre_completo, username, password, rol, curso_asignado) VALUES (?, ?, ?, ?, ?)",
                         (nombre_completo, username, password, rol, curso_asignado))
            flash('Maestro registrado.', 'success')
            
        conn.commit()
        conn.close()
        return redirect(url_for('registrar_usuario'))
    
    maestros = conn.execute("SELECT * FROM usuarios WHERE LOWER(rol) = 'maestro'").fetchall()
    conn.close()
    return render_template('registrar_usuario.html', maestros=maestros, maestro_a_editar=maestro_a_editar)

@app.route('/eliminar_usuario/<int:id>', methods=['POST', 'GET'])
def eliminar_usuario(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Maestro eliminado.', 'success')
    return redirect(url_for('registrar_usuario'))

@app.route('/menu_viejo')
@app.route('/acceso_menu_viejo')
def menu_viejo():
    if session.get('rol') not in ['oficina', 'admin']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('menu'))
        
    conn = get_db_connection()
    try:
        total_estudiantes = conn.execute('SELECT COUNT(*) FROM inscripciones').fetchone()[0]
    except:
        total_estudiantes = 0
    try:
        total_expedientes = conn.execute('SELECT COUNT(*) FROM expedientes_viejos').fetchone()[0]
    except:
        total_expedientes = 0
    try:
        total_usuarios = conn.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
    except:
        total_usuarios = 0
    conn.close()
    
    return render_template('menu_viejo.html', 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios)

@app.route('/expediente-viejo')
def expediente_viejo():
    if session.get('rol') not in ['oficina', 'admin']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('menu'))
        
    conexion = get_db_connection()
    expedientes = conexion.execute('SELECT * FROM expedientes_viejos').fetchall()
    
    total_estudiantes = conexion.execute("SELECT COUNT(*) FROM inscripciones").fetchone()[0]
    total_expedientes = conexion.execute("SELECT COUNT(*) FROM expedientes_viejos").fetchone()[0]
    total_usuarios = conexion.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    conexion.close()
    
    return render_template('expediente_viejos.html', 
                           expedientes=expedientes, 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios)

@app.route('/registrar_expediente_viejo')
def registrar_expediente_viejo():
    if session.get('rol') not in ['oficina', 'admin']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('menu'))
        
    conexion = get_db_connection()
    ultimo = conexion.execute('SELECT "Unnamed: 5" FROM expedientes_viejos WHERE "Unnamed: 5" LIKE \'F-%\' ORDER BY CAST(SUBSTR("Unnamed: 5", 3) AS INTEGER) DESC LIMIT 1').fetchone()
    
    siguiente_ficha = "F-001"
    if ultimo and ultimo[0]:
        try:
            prefix, num_str = str(ultimo[0]).strip().split('-', 1)
            siguiente_ficha = f"{prefix}-{int(num_str) + 1:03d}"
        except ValueError:
            siguiente_ficha = "F-001"

    total_estudiantes = conexion.execute("SELECT COUNT(*) FROM inscripciones").fetchone()[0]
    total_expedientes = conexion.execute("SELECT COUNT(*) FROM expedientes_viejos").fetchone()[0]
    total_usuarios = conexion.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    conexion.close()
    
    return render_template('registrar_expediente_viejo.html', 
                           ficha=siguiente_ficha, 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios)

@app.route('/guardar_expediente_viejo', methods=['POST'])
def guardar_expediente_viejo():
    if session.get('rol') not in ['oficina', 'admin']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('menu'))
        
    ficha = request.form.get('ficha')
    nombre = request.form.get('nombre')
    anio_escolar = request.form.get('anio_escolar')
    
    conexion = get_db_connection()
    conexion.execute('INSERT INTO expedientes_viejos ("Unnamed: 3", "Unnamed: 4", "Unnamed: 5") VALUES (?, ?, ?)', (nombre, anio_escolar, ficha))
    conexion.commit()
    conexion.close()
    
    flash('¡Expediente registrado!', 'success')
    return redirect(url_for('registrar_expediente_viejo'))




if __name__ == '__main__':
    app.run(debug=True)