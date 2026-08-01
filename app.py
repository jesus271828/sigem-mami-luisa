import os
import base64
import sqlite3
from flask import Flask, render_template, make_response, request, redirect, url_for, session, flash, send_file
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename
import psycopg2
import json
import time
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from google.genai import types


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE_URL = os.environ.get('DATABASE_URL')

class PostgresCursorWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def execute(self, query, params=None):
        if params:
            # Reemplazo seguro de '?' por '%s' para compatibilidad PostgreSQL
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

init_db()

# --- RUTA PRINCIPAL (INDEX Y MENU) ---
@app.route('/')
@app.route('/menu')
def index():
    usuario_actual = session.get('usuario')
    if not usuario_actual:
        flash('Por favor inicie sesión.', 'danger')
        return redirect(url_for('login'))
        
    is_postgres = DATABASE_URL is not None
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0

    conexion = get_db_connection()
    try:
        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT COUNT(*) as total FROM estudiantes")
            total_estudiantes = cur.fetchone()['total']
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'expedientes_viejos')")
            if cur.fetchone()['exists']:
                cur.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
                total_expedientes = cur.fetchone()['total']
            else:
                cur.execute("SELECT COUNT(*) as total FROM inscripciones")
                total_expedientes = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur.fetchone()['total']
            cur.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM estudiantes")
            total_estudiantes = conexion.fetchone()[0]
            
            cursor_chk = conexion.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expedientes_viejos'").fetchone()
            if cursor_chk:
                conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
                total_expedientes = conexion.fetchone()[0]
            else:
                conexion.execute("SELECT COUNT(*) FROM inscripciones")
                total_expedientes = conexion.fetchone()[0]
                
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]
    except Exception as e:
        print(f"--- ERROR AL CONTAR EN EL MENÚ PRINCIPAL: {e}")
    finally:
        conexion.close()
    
    return render_template('menu.html', 
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
            cursor = conn
            cursor.execute('SELECT username, rol, nombre_completo, curso_asignado FROM usuarios WHERE username = ? AND password = ?', (usuario_ingresado, password))
            row = cursor.fetchone()
            
            if row:
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

@app.route('/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        import base64

        def guardar_archivo(input_name):
            file = request.files.get(input_name)
            if file and file.filename != '':
                # Lee los bytes de la imagen y los convierte a texto Base64 para guardarlos en la BD
                file_bytes = file.read()
                encoded = base64.b64encode(file_bytes).decode('utf-8')
                return encoded
            return None

        # Captura de datos generales del formulario
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

        # Datos de Padre, Madre y Tutor
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

        # Con quién vive y Responsable Económico
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

        # Bucle dinámico para las 5 personas autorizadas
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

        conexion = None
        try:
            conexion = get_db_connection()
            
            # 1. Insertar en tabla estudiantes
            conexion.execute('''
                INSERT INTO estudiantes (nombres, apellidos, id_estudiante, grado, foto_estudiante_cedula)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombres, apellidos, id_estudiante, grado, foto_estudiante_cedula))
            
            # 2. Recalcular número de orden global alfabéticamente
            conexion.execute("SELECT id FROM estudiantes ORDER BY nombres ASC, apellidos ASC")
            registros_estudiantes = conexion.fetchall()
            for indice, reg in enumerate(registros_estudiantes, start=1):
                reg_id = reg['id'] if isinstance(reg, dict) or hasattr(reg, 'keys') else reg[0]
                conexion.execute("UPDATE estudiantes SET numero_orden = ? WHERE id = ?", (indice, reg_id))

            # 3. Insertar en tabla autorizados
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

            # 4. Insertar en tabla inscripciones generales
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
            flash('¡Estudiante inscrito y guardado correctamente en todas las tablas!', 'success')
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"--- ERROR CRÍTICO EN INSCRIPCIÓN: {e}")
            flash('Hubo un error al guardar los datos.', 'danger')
        finally:
            if conexion:
                conexion.close()

        return redirect(url_for('inscripcion'))

    # Método GET: Consultar los contadores reales en la base de datos de forma segura
    is_postgres = DATABASE_URL is not None
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0

    conexion = get_db_connection()
    try:
        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT COUNT(*) as total FROM estudiantes")
            total_estudiantes = cur.fetchone()['total']
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'expedientes_viejos')")
            if cur.fetchone()['exists']:
                cur.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
                total_expedientes = cur.fetchone()['total']
            else:
                cur.execute("SELECT COUNT(*) as total FROM inscripciones")
                total_expedientes = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur.fetchone()['total']
            cur.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM estudiantes")
            total_estudiantes = conexion.fetchone()[0]
            
            cursor_chk = conexion.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expedientes_viejos'").fetchone()
            if cursor_chk:
                conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
                total_expedientes = conexion.fetchone()[0]
            else:
                conexion.execute("SELECT COUNT(*) FROM inscripciones")
                total_expedientes = conexion.fetchone()[0]
                
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]
    except Exception as e:
        print(f"--- ERROR EXACTO AL CONTAR EN INSCRIPCIÓN: {e}")
    finally:
        conexion.close()

    return render_template(
        'inscripcion.html', 
        total_estudiantes=total_estudiantes, 
        total_expedientes=total_expedientes, 
        total_usuarios=total_usuarios
    )

@app.route('/inscripcion-publica', methods=['GET', 'POST'])
def inscripcion_publica():
    if request.method == 'POST':
        import base64

        def guardar_archivo(input_name):
            file = request.files.get(input_name)
            if file and file.filename != '':
                # Leer los bytes del archivo cargado y convertirlos a Base64
                file_bytes = file.read()
                if file_bytes:
                    encoded = base64.b64encode(file_bytes).decode('utf-8')
                    # Detectar el tipo MIME básico o por defecto usar jpeg
                    mime = file.mimetype or 'image/jpeg'
                    return f"data:{mime};base64,{encoded}"
            return None

        # Captura de datos generales del formulario
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

        # Datos de Padre, Madre y Tutor
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

        # Con quién vive y Responsable Económico
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

        # Bucle dinámico para las 5 personas autorizadas
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

        conexion = None
        try:
            conexion = get_db_connection()
            
            # 1. Insertar en tabla estudiantes
            conexion.execute('''
                INSERT INTO estudiantes (nombres, apellidos, id_estudiante, grado, foto_estudiante_cedula)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombres, apellidos, id_estudiante, grado, foto_estudiante_cedula))
            
            # 2. Recalcular número de orden global alfabéticamente
            conexion.execute("SELECT id FROM estudiantes ORDER BY nombres ASC, apellidos ASC")
            registros_estudiantes = conexion.fetchall()
            for indice, reg in enumerate(registros_estudiantes, start=1):
                reg_id = reg['id'] if isinstance(reg, dict) or hasattr(reg, 'keys') else reg[0]
                conexion.execute("UPDATE estudiantes SET numero_orden = ? WHERE id = ?", (indice, reg_id))

            # 3. Insertar en tabla autorizados
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

            # 4. Insertar en tabla inscripciones generales
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
            flash('¡Formulario enviado con éxito! Sus datos han sido registrados correctamente en el sistema.', 'success')
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"--- ERROR CRÍTICO EN INSCRIPCIÓN PÚBLICA: {e}")
            flash('Hubo un error al enviar el formulario. Por favor intente de nuevo.', 'danger')
        finally:
            if conexion:
                conexion.close()

        return redirect(url_for('inscripcion_publica'))

    # Método GET: Renderiza el archivo HTML del formulario público para los padres
    return render_template('inscripcion_publica.html')

# --- BÚSQUEDA Y OTROS MÓDULOS ---
@app.route('/menu_buscar')
def menu_buscar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    # Permitir acceso tanto a admin como a oficina (o maestros si lo requieres)
    rol_actual = str(session.get('rol', '')).lower()
    if rol_actual not in ['admin', 'oficina']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    try:
        total_estudiantes = conn.execute('SELECT COUNT(*) FROM inscripciones').fetchone()
        total_estudiantes = total_estudiantes['total'] if isinstance(total_estudiantes, dict) else total_estudiantes[0]
    except:
        total_estudiantes = 0
    try:
        total_expedientes = conn.execute('SELECT COUNT(*) FROM expedientes_viejos').fetchone()
        total_expedientes = total_expedientes['total'] if isinstance(total_expedientes, dict) else total_expedientes[0]
    except:
        total_expedientes = 0
    try:
        total_usuarios = conn.execute('SELECT COUNT(*) FROM usuarios').fetchone()
        total_usuarios = total_usuarios['total'] if isinstance(total_usuarios, dict) else total_usuarios[0]
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
        
    conexion = get_db_connection()
    autorizados = []
    criterio = request.form.get('criterio', '') or request.args.get('criterio', '')
    is_postgres = DATABASE_URL is not None

    try:
        if request.method == 'POST' or criterio:
            criterio_limpio = criterio.replace('-', '').strip()
            like_c = f"%{criterio}%"
            like_limpio = f"%{criterio_limpio}%"

            if is_postgres:
                query = """
                    SELECT a.*, i.nombres, i.apellidos, i.grado 
                    FROM autorizados a
                    LEFT JOIN inscripciones i ON a.id_estudiante = i.id_estudiante
                    WHERE REPLACE(a.cedula, '-', '') ILIKE %s 
                       OR a.nombre_completo ILIKE %s 
                       OR a.id_estudiante ILIKE %s
                       OR i.nombres ILIKE %s 
                       OR i.apellidos ILIKE %s
                """
                params = [like_limpio, like_c, like_c, like_c, like_c]
                cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(query, params)
                autorizados = cur.fetchall()
                cur.close()
            else:
                query = """
                    SELECT a.*, i.nombres, i.apellidos, i.grado 
                    FROM autorizados a
                    LEFT JOIN inscripciones i ON a.id_estudiante = i.id_estudiante
                    WHERE REPLACE(a.cedula, '-', '') LIKE ? 
                       OR a.nombre_completo LIKE ? 
                       OR a.id_estudiante LIKE ?
                       OR i.nombres LIKE ? 
                       OR i.apellidos LIKE ?
                """
                params = [like_limpio, like_c, like_c, like_c, like_c]
                conexion.execute(query, params)
                autorizados = conexion.fetchall()

    except Exception as e:
        print("--- ERROR EN BUSCAR AUTORIZADO:", e)
    finally:
        conexion.close()

    return render_template('buscar_autorizado.html', autorizados=autorizados, criterio=criterio)


@app.route('/listado-estudiantes')
def listado_estudiantes():
    if 'usuario' not in session:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
        
    usuario_actual = session.get('usuario')
    rol_actual = session.get('rol')
    
    conn = get_db_connection()
    if rol_actual in ['oficina', 'admin']:
        estudiantes = conn.execute('SELECT * FROM inscripciones').fetchall()
    else:
        estudiantes = conn.execute('SELECT * FROM inscripciones WHERE maestro = ?', (usuario_actual,)).fetchall()
    conn.close()
    
    return render_template('listado_estudiantes.html', estudiantes=estudiantes)


@app.route('/buscar_estudiante', methods=['GET', 'POST'])
def buscar_estudiante():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    conexion = get_db_connection()
    estudiantes = []
    grados_disponibles = []
    is_postgres = DATABASE_URL is not None

    # Capturamos tanto si viene por GET (args) como por POST (form)
    criterio = request.form.get('criterio', '') or request.args.get('criterio', '')
    grado_filtro = request.form.get('grado_filtro', '') or request.args.get('grado_filtro', '')

    try:
        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT DISTINCT grado FROM inscripciones WHERE grado IS NOT NULL AND grado != ''")
            grados_res = cur.fetchall()
            cur.close()
        else:
            conexion.execute("SELECT DISTINCT grado FROM inscripciones WHERE grado IS NOT NULL AND grado != ''")
            grados_res = conexion.fetchall()
            
        grados_disponibles = [g['grado'] if isinstance(g, dict) else g[0] for g in grados_res]

        if is_postgres:
            query = "SELECT id_estudiante, nombres, apellidos, grado FROM inscripciones WHERE 1=1"
            params = []
            if criterio:
                query += " AND (id_estudiante ILIKE %s OR nombres ILIKE %s OR apellidos ILIKE %s)"
                like_c = f"%{criterio}%"
                params.extend([like_c, like_c, like_c])
            if grado_filtro:
                query += " AND grado = %s"
                params.append(grado_filtro)
            
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params)
            estudiantes = cur.fetchall()
            cur.close()
        else:
            query = "SELECT id_estudiante, nombres, apellidos, grado FROM inscripciones WHERE 1=1"
            params = []
            if criterio:
                query += " AND (id_estudiante LIKE ? OR nombres LIKE ? OR apellidos LIKE ?)"
                like_c = f"%{criterio}%"
                params.extend([like_c, like_c, like_c])
            if grado_filtro:
                query += " AND grado = ?"
                params.append(grado_filtro)
                
            conexion.execute(query, params)
            estudiantes = conexion.fetchall()

    except Exception as e:
        print("--- ERROR EN BUSCAR ESTUDIANTE:", e)
    finally:
        conexion.close()

    return render_template(
        'buscar_estudiante.html', 
        estudiantes=estudiantes, 
        grados_disponibles=grados_disponibles,
        criterio=criterio,
        grado_filtro=grado_filtro
    )

@app.route('/generar_pdf/<path:id_estudiante>')
def generar_pdf(id_estudiante):
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    conexion = get_db_connection()
    estudiante = None
    autorizados = []

    try:
        conexion.execute("SELECT * FROM inscripciones")
        filas = conexion.fetchall()
        
        for fila in filas:
            valores = list(fila.values()) if isinstance(fila, dict) else list(fila)
            if len(valores) >= 4 and str(valores[3]).strip() == str(id_estudiante).strip():
                estudiante = fila
                break

        if estudiante:
            valores_est = list(estudiante.values()) if isinstance(estudiante, dict) else list(estudiante)
            id_real_estudiante = valores_est[3]
            
            conexion.execute("SELECT * FROM autorizados WHERE id_estudiante = ?", (str(id_real_estudiante),))
            autorizados = conexion.fetchall()

    except Exception as e:
        print("--- ERROR CRÍTICO EN PDF:", e)
        estudiante = None
    finally:
        conexion.close()
    
    if not estudiante:
        return f"No se encontró ninguna inscripción para el ID: {id_estudiante}", 404

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
def menu_viejo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    rol_actual = session.get('rol', '').lower()
    if 'maestro' in rol_actual or rol_actual == 'profesor':
        flash('Acceso denegado. Los maestros no tienen permiso para entrar aquí.', 'danger')
        return redirect(url_for('menu'))

    conexion = get_db_connection()
    is_postgres = DATABASE_URL is not None
    
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0

    try:
        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT COUNT(*) as total FROM estudiantes")
            total_estudiantes = cur.fetchone()['total']
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'expedientes_viejos')")
            if cur.fetchone()['exists']:
                cur.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
                total_expedientes = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur.fetchone()['total']
            cur.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM estudiantes")
            total_estudiantes = conexion.fetchone()[0]
            
            cursor_chk = conexion.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expedientes_viejos'").fetchone()
            if cursor_chk:
                conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
                total_expedientes = conexion.fetchone()[0]
                
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]
    except Exception as e:
        print(f"Error cargando contadores: {e}")
    finally:
        conexion.close()

    return render_template('menu_viejo.html', 
                           total_estudiantes=total_estudiantes,
                           total_expedientes=total_expedientes,
                           total_usuarios=total_usuarios)

@app.route('/expediente-viejo', methods=['GET', 'POST'])
def expediente_viejo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    resultados = []
    conexion = get_db_connection()
    is_postgres = DATABASE_URL is not None
    
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0

    try:
        criterio = request.form.get('criterio', '').strip() if request.method == 'POST' else ''

        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT COUNT(*) as total FROM estudiantes")
            total_estudiantes = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
            total_expedientes = cur.fetchone()['total']
            
            if criterio:
                cur.execute("""
                    SELECT * FROM expedientes_viejos 
                    WHERE "Unnamed: 3" ILIKE %s OR "Unnamed: 4" ILIKE %s OR "Unnamed: 5" ILIKE %s
                """, (f'%{criterio}%', f'%{criterio}%', f'%{criterio}%'))
            else:
                cur.execute("SELECT * FROM expedientes_viejos LIMIT 100")
            resultados = cur.fetchall()
            cur.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM estudiantes")
            total_estudiantes = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
            total_expedientes = conexion.fetchone()[0]
            
            if criterio:
                conexion.execute("""
                    SELECT * FROM expedientes_viejos 
                    WHERE "Unnamed: 3" LIKE ? OR "Unnamed: 4" LIKE ? OR "Unnamed: 5" LIKE ?
                """, (f'%{criterio}%', f'%{criterio}%', f'%{criterio}%'))
            else:
                conexion.execute("SELECT * FROM expedientes_viejos LIMIT 100")
            resultados = conexion.fetchall()
                
    except Exception as e:
        print("--- ERROR DETALLADO EN EXPEDIENTE VIEJO ---")
        resultados = []
    finally:
        conexion.close()

    return render_template('expediente_viejos.html', 
                           expedientes=resultados,
                           total_estudiantes=total_estudiantes,
                           total_expedientes=total_expedientes,
                           total_usuarios=total_usuarios)

@app.route('/registrar_expediente_viejo', methods=['GET'])
def registrar_expediente_viejo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    if session.get('rol', '').lower() not in ['oficina', 'admin']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('menu_viejo'))
        
    conexion = get_db_connection()
    is_postgres = DATABASE_URL is not None
    
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0
    siguiente_ficha = "F-1"

    try:
        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT COUNT(*) as total FROM estudiantes")
            total_estudiantes = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur.fetchone()['total']
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'expedientes_viejos')")
            if cur.fetchone()['exists']:
                cur.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
                total_expedientes = cur.fetchone()['total']
                
                cur.execute('SELECT "Unnamed: 5" FROM expedientes_viejos ORDER BY id DESC LIMIT 1')
                ultimo = cur.fetchone()
                if ultimo and ultimo['Unnamed: 5']:
                    val = str(ultimo['Unnamed: 5']).strip()
                    import re
                    numeros = re.findall(r'\d+', val)
                    if numeros:
                        num_siguiente = int(numeros[-1]) + 1
                        siguiente_ficha = f"F-{num_siguiente}"
            cur.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM estudiantes")
            total_estudiantes = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]
            
            cursor_chk = conexion.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expedientes_viejos'").fetchone()
            if cursor_chk:
                conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
                total_expedientes = conexion.fetchone()[0]
                
                cursor_f = conexion.execute('SELECT "Unnamed: 5" FROM expedientes_viejos ORDER BY id DESC LIMIT 1').fetchone()
                if cursor_f and cursor_f[0]:
                    val = str(cursor_f[0]).strip()
                    import re
                    numeros = re.findall(r'\d+', val)
                    if numeros:
                        num_siguiente = int(numeros[-1]) + 1
                        siguiente_ficha = f"F-{num_siguiente}"
    except Exception as e:
        print(f"Error cargando ficha: {e}")
    finally:
        conexion.close()

    return render_template('registrar_expediente_viejo.html',
                           total_estudiantes=total_estudiantes,
                           total_expedientes=total_expedientes,
                           total_usuarios=total_usuarios,
                           siguiente_ficha=siguiente_ficha)


@app.route('/guardar_expediente_viejo', methods=['POST'])
def guardar_expediente_viejo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    ficha = request.form.get('ficha', '')
    nombre = request.form.get('nombre', '')
    ano_escolar = request.form.get('anio_escolar', '')
    
    conexion = get_db_connection()
    is_postgres = DATABASE_URL is not None
    
    try:
        if is_postgres:
            cur = conexion.conn.cursor()
            cur.execute('INSERT INTO expedientes_viejos ("Unnamed: 3", "Unnamed: 4", "Unnamed: 5") VALUES (%s, %s, %s)', 
                        (nombre, ano_escolar, ficha))
            conexion.conn.commit()
            cur.close()
        else:
            conexion.execute('INSERT INTO expedientes_viejos ("Unnamed: 3", "Unnamed: 4", "Unnamed: 5") VALUES (?, ?, ?)', 
                             (nombre, ano_escolar, ficha))
            conexion.commit()
            
        flash('¡Expediente registrado correctamente!', 'success')
    except Exception as e:
        flash(f'Error al guardar el expediente: {e}', 'danger')
    finally:
        conexion.close()
        
    return redirect(url_for('registrar_expediente_viejo'))

@app.route('/ver_estructura_db')
def ver_estructura_db():
    conexion = get_db_connection()
    try:
        conexion.execute("SELECT * FROM inscripciones LIMIT 1")
        fila = conexion.fetchone()
        if fila:
            f_dict = dict(fila) if isinstance(fila, dict) else dict(zip([column[0] for column in conexion.description], fila))
            return f_dict
        return "No hay registros en inscripciones"
    finally:
        conexion.close()

import os
import json
import base64
import requests
from flask import Flask, request, jsonify

@app.route('/api/escanear-ficha', methods=['POST'])
def escanear_ficha():
    if 'ficha' not in request.files:
        return jsonify({'success': False, 'error': 'No se encontró la imagen'}), 400
    
    file = request.files['ficha']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'}), 400

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        image_bytes = file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        mime_type = file.content_type or "image/jpeg"

        # Usamos la versión 'v1' de la API con el modelo estable
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": """Analiza esta imagen de una ficha de inscripción escolar y extrae la información en formato JSON estricto. 
                        Las llaves del JSON deben coincidir exactamente con los nombres de los inputs del formulario:
                        {
                            "anio_escolar": "", "fecha_inscripcion": "", "id_estudiante": "", "nombres": "", 
                            "apellidos": "", "grado": "", "fecha_nacimiento": "", "edad": "", "sexo": "", 
                            "nacionalidad": "", "lugar_nac": "", "direccion": "", "cant_hermanos": "", 
                            "edades_hermanos": "", "lugar_ocupa": "", "tipo_sangre": "", "seguro_medico": "", 
                            "alergias": "", "medicamentos": "", "medico_pediatra": "", "centro_medico": "", 
                            "emergencia_tel": "", "emergencia_nombre": "", "emergencia_parentesco": ""
                        }
                        Si algún dato no está visible o legible, déjalo como un string vacío "". Devuelve únicamente el objeto JSON puro sin markdown."""
                    },
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_b64
                        }
                    }
                ]
            }]
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f"API Error: {response.text}"}), 500

        res_json = response.json()
        texto_respuesta = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if texto_respuesta.startswith("```json"):
            texto_respuesta = texto_respuesta[7:-3].strip()
        elif texto_respuesta.startswith("```"):
            texto_respuesta = texto_respuesta[3:-3].strip()
            
        datos_extraidos = json.loads(texto_respuesta)
        return jsonify({'success': True, 'data': datos_extraidos})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    
    
if __name__ == '__main__':
    app.run(debug=True)