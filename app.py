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
        
        user = None
        try:
            conn = get_db_connection()
            is_postgres = DATABASE_URL is not None
            
            if is_postgres:
                cur = conn.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute('SELECT username, rol, nombre_completo, curso_asignado FROM usuarios WHERE username = %s AND password = %s', (usuario_ingresado, password))
                row = cur.fetchone()
                cur.close()
                if row:
                    user = dict(row)
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute('SELECT username, rol, nombre_completo, curso_asignado FROM usuarios WHERE username = ? AND password = ?', (usuario_ingresado, password))
                row = cur.fetchone()
                cur.close()
                if row:
                    user = {
                        'username': row['username'],
                        'rol': row['rol'],
                        'nombre_completo': row['nombre_completo'],
                        'curso_asignado': row['curso_asignado'] if row['curso_asignado'] else ''
                    }
            conn.close()
        except Exception as e:
            print("Error detallado en login:", e)
            user = None
        
        if user:
            session['usuario'] = user.get('username', '')
            session['rol'] = user.get('rol', '')
            session['nombre_completo'] = user.get('nombre_completo', '')
            session['curso_asignado'] = user.get('curso_asignado', '')
            return redirect('/menu')
        else:
            flash("Usuario o contraseña incorrectos", "danger")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/buscar_estudiante/<id_estudiante>', methods=['GET'])
def api_buscar_estudiante(id_estudiante):
    if 'usuario' not in session:
        return jsonify({'encontrado': False})
    
    conexion = get_db_connection()
    # Si usas psycopg2 (PostgreSQL en Render), ajustamos para que devuelva diccionarios
    cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) if hasattr(conexion, 'cursor') else conexion
    
    try:
        cursor.execute("SELECT * FROM inscripciones WHERE id_estudiante = %s", (id_estudiante,))
        estudiante = cursor.fetchone()
        
        if estudiante:
            # Convertimos a dict estándar por seguridad
            datos_dict = dict(estudiante)
            return jsonify({'encontrado': True, 'datos': datos_dict})
        else:
            return jsonify({'encontrado': False})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'encontrado': False, 'error': str(e)})
    finally:
        if conexion:
            conexion.close()

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import base64

# Nota: Asegúrate de mantener tu inicialización de 'app' y tu función get_db_connection() tal como las tienes configuradas.

@app.route('/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'usuario' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. No tienes permisos para realizar nuevas inscripciones.', 'danger')
        return redirect(url_for('menu')) 

    if request.method == 'POST':
        def guardar_archivo(input_name):
            file = request.files.get(input_name)
            if file and file.filename != '':
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
            cursor_check = conexion if hasattr(conexion, 'execute') else conexion.cursor()
            cursor_check.execute("SELECT COUNT(*) FROM inscripciones WHERE id_estudiante = %s", (id_estudiante,))
            resultado_existe = cursor_check.fetchone()
            
            existe_en_db = False
            if resultado_existe:
                if isinstance(resultado_existe, dict) or hasattr(resultado_existe, 'keys'):
                    existe_en_db = list(resultado_existe.values())[0] > 0
                else:
                    existe_en_db = resultado_existe[0] > 0

            if existe_en_db:
                # --- ACTUALIZAR REGISTRO EXISTENTE (Incluyendo sexo) ---
                conexion.execute('''
                    UPDATE estudiantes 
                    SET nombres = ?, apellidos = ?, grado = ?, sexo = ?, foto_estudiante_cedula = ?
                    WHERE id_estudiante = ?
                ''', (nombres, apellidos, grado, sexo, foto_estudiante_cedula, id_estudiante))
                
                conexion.execute('''
                    UPDATE autorizados 
                    SET nombres = ?, apellidos = ?, grado = ?, foto_estudiante_cedula = ?,
                        padre_nombre = ?, padre_cedula = ?, foto_padre_cedula = ?, padre_tel_personal = ?, padre_tel_trabajo = ?,
                        madre_nombre = ?, madre_cedula = ?, foto_madre_cedula = ?, madre_tel_personal = ?, madre_tel_trabajo = ?,
                        tutor_nombre = ?, tutor_cedula = ?, foto_tutor_cedula = ?, tutor_tel_personal = ?, tutor_tel_trabajo = ?,
                        aut_nombre_1 = ?, aut_cedula_1 = ?, aut_parentesco_1 = ?, aut_tel_1 = ?, foto_aut_cedula_1 = ?,
                        aut_nombre_2 = ?, aut_cedula_2 = ?, aut_parentesco_2 = ?, aut_tel_2 = ?, foto_aut_cedula_2 = ?,
                        aut_nombre_3 = ?, aut_cedula_3 = ?, aut_parentesco_3 = ?, aut_tel_3 = ?, foto_aut_cedula_3 = ?,
                        aut_nombre_4 = ?, aut_cedula_4 = ?, aut_parentesco_4 = ?, aut_tel_4 = ?, foto_aut_cedula_4 = ?,
                        aut_nombre_5 = ?, aut_cedula_5 = ?, aut_parentesco_5 = ?, aut_tel_5 = ?, foto_aut_cedula_5 = ?
                    WHERE id_estudiante = ?
                ''', (
                    nombres, apellidos, grado, foto_estudiante_cedula,
                    padre_nombre, padre_cedula, foto_padre_cedula, padre_tel_personal, padre_tel_trabajo,
                    madre_nombre, madre_cedula, foto_madre_cedula, madre_tel_personal, madre_tel_trabajo,
                    tutor_nombre, tutor_cedula, foto_tutor_cedula, tutor_tel_personal, tutor_tel_trabajo,
                    aut_data['aut_nombre_1'], aut_data['aut_cedula_1'], aut_data['aut_parentesco_1'], aut_data['aut_tel_1'], aut_data['foto_aut_cedula_1'],
                    aut_data['aut_nombre_2'], aut_data['aut_cedula_2'], aut_data['aut_parentesco_2'], aut_data['aut_tel_2'], aut_data['foto_aut_cedula_2'],
                    aut_data['aut_nombre_3'], aut_data['aut_cedula_3'], aut_data['aut_parentesco_3'], aut_data['aut_tel_3'], aut_data['foto_aut_cedula_3'],
                    aut_data['aut_nombre_4'], aut_data['aut_cedula_4'], aut_data['aut_parentesco_4'], aut_data['aut_tel_4'], aut_data['foto_aut_cedula_4'],
                    aut_data['aut_nombre_5'], aut_data['aut_cedula_5'], aut_data['aut_parentesco_5'], aut_data['aut_tel_5'], aut_data['foto_aut_cedula_5'],
                    id_estudiante
                ))

                conexion.execute('''
                    UPDATE inscripciones 
                    SET anio_escolar = ?, fecha_inscripcion = ?, nombres = ?, apellidos = ?, grado = ?, 
                        fecha_nacimiento = ?, edad = ?, sexo = ?, nacionalidad = ?, lugar_nac = ?, direccion = ?, cant_hermanos = ?, 
                        edades_hermanos = ?, lugar_ocupa = ?, tipo_sangre = ?, seguro_medico = ?, foto_estudiante_cedula = ?, 
                        alergias = ?, medicamentos = ?, medico_pediatra = ?, centro_medico = ?, emergencia_tel = ?, 
                        emergencia_nombre = ?, emergencia_parentesco = ?,
                        padre_nombre = ?, padre_sector = ?, padre_direccion = ?, padre_profesion = ?, padre_cedula = ?, 
                        foto_padre_cedula = ?, padre_nivel = ?, padre_religion = ?, padre_tel_personal = ?, padre_tel_trabajo = ?, padre_correo = ?,
                        madre_nombre = ?, madre_sector = ?, madre_direccion = ?, madre_profesion = ?, madre_cedula = ?, 
                        foto_madre_cedula = ?, madre_nivel = ?, madre_religion = ?, madre_tel_personal = ?, madre_tel_trabajo = ?, madre_correo = ?,
                        tutor_nombre = ?, tutor_sector = ?, tutor_direccion = ?, tutor_profesion = ?, tutor_cedula = ?, 
                        foto_tutor_cedula = ?, tutor_nivel = ?, tutor_religion = ?, tutor_tel_personal = ?, tutor_tel_trabajo = ?, tutor_correo = ?,
                        vive_nombres = ?, vive_parentesco = ?, vive_cedula = ?, foto_vive_cedula = ?, vive_direccion = ?, 
                        vive_sector = ?, vive_profesion = ?, vive_nivel = ?, vive_religion = ?, vive_tel_personal = ?, vive_tel_trabajo = ?, vive_correo = ?,
                        econ_nombres = ?, econ_parentesco = ?, econ_cedula = ?, foto_econ_cedula = ?, econ_direccion = ?, 
                        econ_sector = ?, econ_profesion = ?, econ_lugar_trabajo = ?, econ_tel_personal = ?, econ_tel_trabajo = ?, econ_correo = ?,
                        aut_nombre_1 = ?, aut_cedula_1 = ?, aut_parentesco_1 = ?, aut_tel_1 = ?, foto_aut_cedula_1 = ?,
                        aut_nombre_2 = ?, aut_cedula_2 = ?, aut_parentesco_2 = ?, aut_tel_2 = ?, foto_aut_cedula_2 = ?,
                        aut_nombre_3 = ?, aut_cedula_3 = ?, aut_parentesco_3 = ?, aut_tel_3 = ?, foto_aut_cedula_3 = ?,
                        aut_nombre_4 = ?, aut_cedula_4 = ?, aut_parentesco_4 = ?, aut_tel_4 = ?, foto_aut_cedula_4 = ?,
                        aut_nombre_5 = ?, aut_cedula_5 = ?, aut_parentesco_5 = ?, aut_tel_5 = ?, foto_aut_cedula_5 = ?,
                        autoriza_medicamentos = ?, autoriza_redes = ?, firma_redes = ?
                    WHERE id_estudiante = ?
                ''', (
                    anio_escolar, fecha_inscripcion, nombres, apellidos, grado, 
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
                    autoriza_medicamentos, autoriza_redes, firma_redes,
                    id_estudiante
                ))
                flash('¡Los datos del estudiante existente fueron actualizados correctamente!', 'success')
            else:
                # --- INSERTAR NUEVO REGISTRO (Incluyendo sexo) ---
                conexion.execute('''
                    INSERT INTO estudiantes (nombres, apellidos, id_estudiante, grado, sexo, foto_estudiante_cedula)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (nombres, apellidos, id_estudiante, grado, sexo, foto_estudiante_cedula))
                
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
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
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
                flash('¡Estudiante inscrito y guardado correctamente en todas las tablas!', 'success')
            
            conexion.execute("SELECT id FROM estudiantes ORDER BY nombres ASC, apellidos ASC")
            registros_estudiantes = conexion.fetchall()
            for indice, reg in enumerate(registros_estudiantes, start=1):
                reg_id = reg['id'] if isinstance(reg, dict) or hasattr(reg, 'keys') else reg[0]
                conexion.execute("UPDATE estudiantes SET numero_orden = ? WHERE id = ?", (indice, reg_id))

            conexion.commit()
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"--- ERROR CRÍTICO EN INSCRIPCIÓN: {e}")
            flash('Hubo un error al guardar los datos.', 'danger')
        finally:
            if conexion:
                conexion.close()

        return redirect(url_for('inscripcion'))

    # Método GET
    conexion = get_db_connection()
    cursor = conexion if hasattr(conexion, 'execute') else conexion.cursor()
    
    def obtener_conteo(query):
        try:
            cursor.execute(query)
            res = cursor.fetchone()
            if not res:
                return 0
            if isinstance(res, dict) or hasattr(res, 'keys'):
                return list(res.values())[0]
            return res[0]
        except Exception:
            return 0

    total_estudiantes = obtener_conteo("SELECT COUNT(*) FROM estudiantes")
    total_expedientes = obtener_conteo("SELECT COUNT(*) FROM expedientes_viejos")
    total_usuarios = obtener_conteo("SELECT COUNT(*) FROM usuarios")

    if conexion:
        conexion.close()

    return render_template('inscripcion.html', 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios)

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

# --- BÚSQUEDA Y OTROS MÓDULOS ---
@app.route('/menu_buscar', methods=['GET'])
def menu_buscar():
    try:
        if 'usuario' not in session:
            return redirect(url_for('login'))
            
        rol_actual = str(session.get('rol', '')).lower().strip()
        if rol_actual not in ['admin', 'oficina']:
            flash('Acceso denegado.', 'danger')
            return redirect('/menu')

        conexion = get_db_connection()
        is_postgres = DATABASE_URL is not None
        total_estudiantes = 0
        total_expedientes = 0
        total_usuarios = 0

        if is_postgres:
            cur_c = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur_c.execute("SELECT COUNT(*) as total FROM inscripciones")
            total_estudiantes = cur_c.fetchone()['total']
            cur_c.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
            total_expedientes = cur_c.fetchone()['total']
            cur_c.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur_c.fetchone()['total']
            cur_c.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM inscripciones")
            total_estudiantes = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
            total_expedientes = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]

        conexion.close()

        return render_template('menu_buscar.html', 
                               total_estudiantes=total_estudiantes, 
                               total_expedientes=total_expedientes, 
                               total_usuarios=total_usuarios)
    except Exception as e:
        print(f"Error en menu_buscar: {e}")
        flash("Ocurrió un error interno en el servidor.", "danger")
        return redirect('/menu')

@app.route('/buscar_autorizado', methods=['GET', 'POST'])
def buscar_autorizado():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    conexion = get_db_connection()
    autorizados = []
    is_postgres = DATABASE_URL is not None
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0

    try:
        if is_postgres:
            cur_c = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur_c.execute("SELECT COUNT(*) as total FROM inscripciones")
            total_estudiantes = cur_c.fetchone()['total']
            cur_c.execute("SELECT COUNT(*) as total FROM expedientes_viejos")
            total_expedientes = cur_c.fetchone()['total']
            cur_c.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur_c.fetchone()['total']
            cur_c.close()
        else:
            conexion.execute("SELECT COUNT(*) FROM inscripciones")
            total_estudiantes = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM expedientes_viejos")
            total_expedientes = conexion.fetchone()[0]
            conexion.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = conexion.fetchone()[0]

        if request.method == 'POST':
            criterio_raw = request.form.get('criterio', '').strip()
            criterio = criterio_raw.lower()
            criterio_limpio = criterio_raw.replace('-', '').lower()

            if is_postgres:
                cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute("SELECT * FROM inscripciones")
                filas = cur.fetchall()
                cur.close()
            else:
                conexion.execute("SELECT * FROM inscripciones")
                filas = conexion.fetchall()

            for fila in filas:
                f_dict = dict(fila) if isinstance(fila, dict) else dict(zip([column[0] for column in conexion.description], fila))
                
                # Campos generales del estudiante
                nombres_est = str(f_dict.get('nombres') or f_dict.get('estudiante_nombre') or '').lower()
                apellidos_est = str(f_dict.get('apellidos') or f_dict.get('estudiante_apellido') or '').lower()
                id_est = str(f_dict.get('id_estudiante') or f_dict.get('id') or '').lower()
                
                # Cédulas de padres o tutores adicionales en la inscripción (si aplican)
                tutor_ced = str(f_dict.get('tutor_cedula') or '').replace('-', '').lower()
                padre_ced = str(f_dict.get('foto_padre_cedula') or '').replace('-', '').lower()
                madre_ced = str(f_dict.get('foto_madre_cedula') or '').replace('-', '').lower()
                est_ced = str(f_dict.get('foto_estudiante_cedula') or '').replace('-', '').lower()

                # Revisar los 5 autorizados
                for i in range(1, 6):
                    nombre_aut = f_dict.get(f'aut_nombre_{i}')
                    cedula_aut_raw = f_dict.get(f'aut_cedula_{i}')
                    
                    if nombre_aut or cedula_aut_raw:
                        nombre_aut_str = str(nombre_aut or '').lower()
                        cedula_aut_str = str(cedula_aut_raw or '')
                        cedula_aut_limpia = cedula_aut_str.replace('-', '').lower()

                        # Validar coincidencia flexible (con o sin guiones, por nombre del niño, del autorizado o cédulas)
                        coincide = (
                            not criterio or
                            criterio in nombre_aut_str or
                            criterio_limpio in cedula_aut_limpia or
                            criterio in nombres_est or
                            criterio in apellidos_est or
                            criterio in id_est or
                            criterio_limpio in tutor_ced or
                            criterio_limpio in padre_ced or
                            criterio_limpio in madre_ced or
                            criterio_limpio in est_ced
                        )

                        if coincide:
                            # Obtener foto del autorizado
                            f_aut = f_dict.get(f'foto_aut_cedula_{i}')
                            if not f_aut and i == 1:
                                f_aut = f_dict.get('foto_padre_cedula') or f_dict.get('foto_madre_cedula')

                            if f_aut and not (str(f_aut).startswith('/9j/') or str(f_aut).startswith('iVBOR') or str(f_aut).startswith('R0lGOD') or str(f_aut).startswith('UklGR')):
                                f_aut = os.path.basename(str(f_aut).replace('\\', '/'))

                            # Obtener foto del estudiante
                            raw_est = (
                                f_dict.get('foto_estudiante_cedula') or 
                                f_dict.get('foto_estudiante') or 
                                f_dict.get('foto') or 
                                f_dict.get('foto_cedula_estudiante')
                            )
                            
                            f_est = ""
                            if raw_est and str(raw_est).lower() not in ['none', '']:
                                if str(raw_est).startswith('/9j/') or str(raw_est).startswith('iVBOR') or str(raw_est).startswith('R0lGOD') or str(raw_est).startswith('UklGR'):
                                    f_est = str(raw_est)
                                else:
                                    f_est = os.path.basename(str(raw_est).replace('\\', '/'))

                            autorizados.append({
                                'nombre_completo': nombre_aut or 'No registrado',
                                'cedula': cedula_aut_raw or 'N/A',
                                'parentesco': f_dict.get(f'aut_parentesco_{i}', 'No especificado'),
                                'foto_autorizado': f_aut,
                                'foto_estudiante': f_est,
                                'nombres': f_dict.get('nombres') or f_dict.get('estudiante_nombre'),
                                'apellidos': f_dict.get('apellidos') or f_dict.get('estudiante_apellido'),
                                'grado': f_dict.get('grado') or f_dict.get('curso'),
                                'id_estudiante': f_dict.get('id_estudiante') or f_dict.get('id')
                            })

    except Exception as e:
        print("--- ERROR EN BUSCAR AUTORIZADO:", e)
    finally:
        conexion.close()

    return render_template('buscar_autorizado.html', 
                           autorizados=autorizados, 
                           total_estudiantes=total_estudiantes, 
                           total_expedientes=total_expedientes, 
                           total_usuarios=total_usuarios)



@app.route('/listado-estudiantes')
def listado_estudiantes():
    if 'usuario' not in session:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
        
    usuario_actual = str(session.get('usuario', '')).strip()
    rol_actual = str(session.get('rol', '')).strip().lower()
    curso_seleccionado = request.args.get('curso', '').strip()
    
    conn = get_db_connection()
    try:
        # Obtenemos la lista de cursos para el selector
        cursos_disponibles = conn.execute('SELECT DISTINCT grado FROM estudiantes WHERE grado IS NOT NULL').fetchall()
        
        if rol_actual in ['oficina', 'admin']:
            if curso_seleccionado:
                rows = conn.execute('''
                    SELECT * FROM estudiantes 
                    WHERE grado = ? 
                    ORDER BY apellidos ASC, nombres ASC
                ''', (curso_seleccionado,)).fetchall()
            else:
                rows = conn.execute('''
                    SELECT * FROM estudiantes 
                    ORDER BY grado ASC, apellidos ASC, nombres ASC
                ''').fetchall()
                
            estudiantes = []
            contador = 1
            grado_anterior = None
            
            for row in rows:
                est = dict(row)
                grado_actual = str(est.get('grado', '')).strip()
                
                if grado_actual != grado_anterior:
                    contador = 1
                    grado_anterior = grado_actual
                
                est['numero_orden'] = contador
                estudiantes.append(est)
                contador += 1
        else:
            usuario_db = conn.execute('''
                SELECT curso_asignado FROM usuarios 
                WHERE username = ?
            ''', (usuario_actual,)).fetchone()
            
            curso_docente = usuario_db['curso_asignado'] if usuario_db and usuario_db['curso_asignado'] else session.get('grado')
            
            if curso_docente:
                rows = conn.execute('''
                    SELECT * FROM estudiantes 
                    WHERE grado = ? 
                    ORDER BY apellidos ASC, nombres ASC
                ''', (curso_docente,)).fetchall()
            else:
                rows = conn.execute('''
                    SELECT * FROM estudiantes 
                    ORDER BY grado ASC, apellidos ASC, nombres ASC
                ''').fetchall()
                
            estudiantes = []
            contador = 1
            for row in rows:
                est = dict(row)
                est['numero_orden'] = contador
                estudiantes.append(est)
                contador += 1
                
    except Exception as e:
        print(f"Error en listado_estudiantes: {e}")
        estudiantes = []
        cursos_disponibles = []
    finally:
        conn.close()
    
    return render_template('listado_estudiantes.html', 
                           estudiantes=estudiantes, 
                           cursos_disponibles=cursos_disponibles, 
                           curso_seleccionado=curso_seleccionado,
                           rol_actual=rol_actual)


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

from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash

@app.route('/asistencia', methods=['GET', 'POST'])
def asistencia():
    if 'usuario' not in session:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
        
    rol_actual = str(session.get('rol', '')).strip().lower()
    if rol_actual not in ['oficina', 'admin']:
        flash('Acceso denegado. Sección exclusiva para personal de oficina.', 'danger')
        return redirect(url_for('menu'))
    
    conn = get_db_connection()
    try:
        cursos_db = conn.execute("SELECT DISTINCT grado FROM estudiantes WHERE grado IS NOT NULL AND TRIM(grado) != '' ORDER BY grado ASC").fetchall()
        grados = [c['grado'] for c in cursos_db]
        
        fecha_actual = request.args.get('fecha', '') or request.form.get('fecha', '')
        if not fecha_actual:
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        if request.method == 'POST':
            grado_seleccionado = request.form.get('grado_actual', '').strip()
            
            estudiantes = conn.execute('''
                SELECT * FROM estudiantes 
                WHERE grado = %s 
                ORDER BY apellidos ASC, nombres ASC
            ''', (grado_seleccionado,)).fetchall()
            
            for est in estudiantes:
                est_id = int(est['id']) 
                estado = request.form.get(f'estado_{est_id}', 'Presente')
                
                existe = conn.execute('SELECT id FROM asistencia WHERE id_estudiante = %s AND fecha = %s', (est_id, fecha_actual)).fetchone()
                if existe:
                    conn.execute('UPDATE asistencia SET estado = %s, grado = %s WHERE id_estudiante = %s AND fecha = %s', (estado, grado_seleccionado, est_id, fecha_actual))
                else:
                    conn.execute('INSERT INTO asistencia (id_estudiante, grado, fecha, estado) VALUES (%s, %s, %s, %s)', (est_id, grado_seleccionado, fecha_actual, estado))
            
            conn.commit()
            flash(f'Asistencia guardada correctamente para el grado {grado_seleccionado}.', 'success')
            return redirect(url_for('asistencia', grado=grado_seleccionado, fecha=fecha_actual))
            
        else:
            grado_seleccionado = request.args.get('grado', '').strip()
            estudiantes = []
            ausentes_hoy = []
            
            if grado_seleccionado:
                rows = conn.execute('''
                    SELECT e.*, a.estado as estado_asistencia 
                    FROM estudiantes e
                    LEFT JOIN asistencia a ON e.id = a.id_estudiante AND a.fecha = %s
                    WHERE e.grado = %s 
                    ORDER BY e.apellidos ASC, e.nombres ASC
                ''', (fecha_actual, grado_seleccionado)).fetchall()
                
                for row in rows:
                    est = dict(row)
                    est['estado_actual'] = est['estado_asistencia'] if est['estado_asistencia'] else 'Presente'
                    estudiantes.append(est)
                
                ausentes_rows = conn.execute('''
                    SELECT e.id, e.nombres, e.apellidos, a.estado 
                    FROM asistencia a
                    JOIN estudiantes e ON a.id_estudiante = e.id
                    WHERE a.grado = %s AND a.fecha = %s AND a.estado IN ('Ausente', 'Tarde')
                    ORDER BY e.apellidos ASC
                ''', (grado_seleccionado, fecha_actual)).fetchall()
                
                for aus in ausentes_rows:
                    ausentes_hoy.append(dict(aus))
                    
    except Exception as e:
        print(f"Error en asistencia: {e}")
        grados = []
        estudiantes = []
        ausentes_hoy = []
        grado_seleccionado = ''
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
    finally:
        conn.close()
        
    return render_template('asistencia.html', 
                           grados=grados, 
                           grado_seleccionado=grado_seleccionado, 
                           fecha_actual=fecha_actual, 
                           estudiantes=estudiantes,
                           ausentes_hoy=ausentes_hoy)

@app.route('/descargar_reporte_ausencias')
def descargar_reporte_ausencias():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    fecha_reporte = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    try:
        # Definir los cursos oficiales de Primaria (1ro a 6to con sus secciones comunes)
        grados_primaria = ['1ro A', '1ro B', '2do A', '2do B', '3ro A', '3ro B', '4to A', '4to B', '5to A', '5to B', '6to A', '6to B']
        
        # Definir los cursos de Inicial
        grados_inicial = ['Párvulos', 'Prekínder – A', 'Prekínder – B', 'Kínder – A', 'Kínder – B', 'Preprimario – A', 'Preprimario – B']

        def procesar_grados(lista_grados):
            resultado = []
            tot_mat_ninos = 0
            tot_mat_ninas = 0
            tot_mat_gral = 0
            tot_asis_ninos = 0
            tot_asis_ninas = 0
            tot_asis_gral = 0

            for grado_nombre in lista_grados:
                # Matrícula Niños
                cur_mn = conn.execute("SELECT COUNT(*) FROM estudiantes WHERE grado = %s AND LOWER(TRIM(sexo)) = 'masculino'", (grado_nombre,))
                res_mn = cur_mn.fetchone()
                mat_ninos = int(res_mn[0] if (isinstance(res_mn, (list, tuple)) or not hasattr(res_mn, 'keys')) else list(res_mn.values())[0])

                # Matrícula Niñas
                cur_mna = conn.execute("SELECT COUNT(*) FROM estudiantes WHERE grado = %s AND LOWER(TRIM(sexo)) = 'femenino'", (grado_nombre,))
                res_mna = cur_mna.fetchone()
                mat_ninas = int(res_mna[0] if (isinstance(res_mna, (list, tuple)) or not hasattr(res_mna, 'keys')) else list(res_mna.values())[0])

                tot_mat = mat_ninos + mat_ninas

                # Asistencia Niños
                cur_an = conn.execute('''
                    SELECT COUNT(*) FROM asistencia a JOIN estudiantes e ON a.id_estudiante = e.id
                    WHERE a.grado = %s AND a.fecha = %s AND a.estado = 'Presente' AND LOWER(TRIM(e.sexo)) = 'masculino'
                ''', (grado_nombre, fecha_reporte))
                res_an = cur_an.fetchone()
                asis_ninos = int(res_an[0] if (isinstance(res_an, (list, tuple)) or not hasattr(res_an, 'keys')) else list(res_an.values())[0])

                # Asistencia Niñas
                cur_ana = conn.execute('''
                    SELECT COUNT(*) FROM asistencia a JOIN estudiantes e ON a.id_estudiante = e.id
                    WHERE a.grado = %s AND a.fecha = %s AND a.estado = 'Presente' AND LOWER(TRIM(e.sexo)) = 'femenino'
                ''', (grado_nombre, fecha_reporte))
                res_ana = cur_ana.fetchone()
                asis_ninas = int(res_ana[0] if (isinstance(res_ana, (list, tuple)) or not hasattr(res_ana, 'keys')) else list(res_ana.values())[0])

                tot_asis = asis_ninos + asis_ninas

                # Ausentes
                ausentes_db = conn.execute('''
                    SELECT e.nombres, e.apellidos FROM asistencia a JOIN estudiantes e ON a.id_estudiante = e.id
                    WHERE a.grado = %s AND a.fecha = %s AND a.estado IN ('Ausente', 'Tarde')
                ''', (grado_nombre, fecha_reporte)).fetchall()
                nombres_ausentes = ", ".join([f"{a['apellidos']} {a['nombres']}" for a in ausentes_db])

                tot_mat_ninos += mat_ninos
                tot_mat_ninas += mat_ninas
                tot_mat_gral += tot_mat
                tot_asis_ninos += asis_ninos
                tot_asis_ninas += asis_ninas
                tot_asis_gral += tot_asis

                resultado.append({
                    'grado': grado_nombre,
                    'mat_ninos': mat_ninos if mat_ninos > 0 else '',
                    'mat_ninas': mat_ninas if mat_ninas > 0 else '',
                    'tot_mat': tot_mat if tot_mat > 0 else '',
                    'asis_ninos': asis_ninos if asis_ninos > 0 else '',
                    'asis_ninas': asis_ninas if asis_ninas > 0 else '',
                    'tot_asis': tot_asis if tot_asis > 0 else '',
                    'ausentes': nombres_ausentes
                })

            totales = {
                'mat_ninos': tot_mat_ninos, 'mat_ninas': tot_mat_ninas, 'tot_mat': tot_mat_gral,
                'asis_ninos': tot_asis_ninos, 'asis_ninas': tot_asis_ninas, 'tot_asis': tot_asis_gral
            }
            return resultado, totales

        datos_primaria, tot_primaria = procesar_grados(grados_primaria)
        datos_inicial, tot_inicial = procesar_grados(grados_inicial)

    finally:
        conn.close()

    return render_template('control_asistencia_pdf.html', 
                           fecha=fecha_reporte,
                           datos_primaria=datos_primaria,
                           tot_primaria=tot_primaria,
                           datos_inicial=datos_inicial,
                           tot_inicial=tot_inicial)

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
                estudiante = dict(fila) if not isinstance(fila, dict) else fila
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

    # Procesar Logo en Base64
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo2.png')
    logo_src = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        logo_src = f"data:image/png;base64,{logo_base64}"
        
    # Procesar la foto desde la columna correcta: foto_estudiante_cedula
    foto_valor = estudiante.get('foto_estudiante_cedula') if isinstance(estudiante, dict) else estudiante['foto_estudiante_cedula'] if 'foto_estudiante_cedula' in estudiante.keys() else None
    foto_base64_src = ""
    
    if foto_valor:
        foto_str = str(foto_valor).strip()
        # Si ya viene guardada como base64 directo en la base de datos
        if foto_str.startswith('/9j/') or foto_str.startswith('data:image'):
            mime = 'image/jpeg' if foto_str.startswith('/9j/') else 'image/png'
            foto_base64_src = foto_str if foto_str.startswith('data:') else f"data:{mime};base64,{foto_str}"
        else:
            # Si guarda una ruta tipo 'uploads/nombre.jpg' o 'nombre.jpg'
            nombre_archivo = foto_str.replace('uploads/', '')
            foto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', nombre_archivo)
            if os.path.exists(foto_path):
                with open(foto_path, "rb") as foto_file:
                    foto_encoded = base64.b64encode(foto_file.read()).decode('utf-8')
                    ext = nombre_archivo.split('.')[-1].lower()
                    mime_type = 'image/png' if ext == 'png' else 'image/jpeg'
                    foto_base64_src = f"data:{mime_type};base64,{foto_encoded}"

    if not isinstance(estudiante, dict):
        estudiante = dict(estudiante)
    
    estudiante['foto_base64'] = foto_base64_src
    
    html = render_template('pdf_ficha.html', estudiante=estudiante, autorizados=autorizados, logo_src=logo_src)
    
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ficha_inscripcion_{id_estudiante}.pdf'
    
    pisa_status = pisa.CreatePDF(html, dest=response.stream)
    
    if pisa_status.err:
        return 'Hubo un error al generar el PDF', 500
        
    return response



@app.route('/menu_notas')
def menu_notas():
    return render_template('menu_notas.html')

import sqlite3
from flask import render_template, request, redirect, url_for, session, flash

@app.route('/notas1', methods=['GET', 'POST'])
def notas1():
    tipo_inf = 'notas1'
    
    conexion = sqlite3.connect('sigem_ml.db')
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    try:
        # CONSULTA DIRECTA: Trae absolutamente todos los estudiantes sin filtros restrictivos
        cursor.execute("""
            SELECT id_estudiante, nombres, apellidos, grado 
            FROM estudiantes 
            ORDER BY apellidos, nombres ASC
        """)
        lista_estudiantes = cursor.fetchall()

        if not lista_estudiantes:
            cursor.close()
            conexion.close()
            return render_template('notas1.html', lista_estudiantes=[], estudiante=None, notas={})

        # Selección del estudiante activo
        id_est_sel = request.args.get('id_estudiante') or request.form.get('id_estudiante')
        
        if id_est_sel:
            estudiante = next((e for e in lista_estudiantes if str(e['id_estudiante']) == str(id_est_sel)), lista_estudiantes[0])
        else:
            estudiante = lista_estudiantes[0]

        # Número de orden generado por su posición en la lista
        indice_en_lista = list(lista_estudiantes).index(estudiante) + 1
        
        estudiante_dict = dict(estudiante)
        estudiante_dict['orden'] = indice_en_lista

        # Guardar datos (POST)
        if request.method == 'POST':
            for campo, valor in request.form.items():
                if campo == 'id_estudiante':
                    continue
                cursor.execute("""
                    INSERT INTO calificaciones_detalle (id_estudiante, tipo_informe, campo_nombre, valor)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id_estudiante, tipo_informe, campo_nombre) 
                    DO UPDATE SET valor = ?
                """, (estudiante['id_estudiante'], tipo_inf, campo, valor, valor))
                
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect(url_for('notas1', id_estudiante=estudiante['id_estudiante']))

        # Cargar notas guardadas (GET)
        cursor.execute("SELECT campo_nombre, valor FROM calificaciones_detalle WHERE id_estudiante = ? AND tipo_informe = ?", 
                       (estudiante['id_estudiante'], tipo_inf))
        resultados = cursor.fetchall()
        notas = {row['campo_nombre']: row['valor'] for row in resultados}

        cursor.close()
        conexion.close()
        
        return render_template('notas1.html', 
                               lista_estudiantes=lista_estudiantes, 
                               estudiante=estudiante_dict, 
                               notas=notas)

    except Exception as e:
        if conexion:
            conexion.close()
        print(f"Error en notas1: {e}")
        return redirect(url_for('index'))
    
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
        
    conexion = get_db_connection()
    is_postgres = DATABASE_URL is not None
    edit_id = request.args.get('edit_id')
    
    maestro_a_editar = None
    maestros = []

    try:
        # Obtener el usuario a editar si existe
        if edit_id:
            if is_postgres:
                cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute("SELECT * FROM usuarios WHERE id = %s", (edit_id,))
                maestro_a_editar = cur.fetchone()
                cur.close()
            else:
                conexion.row_factory = sqlite3.Row
                cursor = conexion.execute("SELECT * FROM usuarios WHERE id = ?", (edit_id,))
                maestro_a_editar = cursor.fetchone()

        if request.method == 'POST':
            nombre_completo = request.form['nombre_completo']
            username = request.form['nombre_usuario']
            password = request.form['contrasena']
            rol = request.form['rol']
            curso_asignado = request.form['curso_asignado']
            id_usuario = request.form.get('id_usuario')

            if id_usuario:
                # Actualizar usuario existente
                if is_postgres:
                    cur = conexion.conn.cursor()
                    cur.execute("UPDATE usuarios SET nombre_completo = %s, username = %s, password = %s, rol = %s, curso_asignado = %s WHERE id = %s",
                                 (nombre_completo, username, password, rol, curso_asignado, id_usuario))
                    conexion.conn.commit()
                    cur.close()
                else:
                    conexion.execute("UPDATE usuarios SET nombre_completo = ?, username = ?, password = ?, rol = ?, curso_asignado = ? WHERE id = ?",
                                     (nombre_completo, username, password, rol, curso_asignado, id_usuario))
                    conexion.commit()
                flash('Maestro actualizado.', 'success')
            else:
                # Insertar nuevo usuario (Sin pasar 'id' para que la base de datos asigne el siguiente automáticamente)
                if is_postgres:
                    cur = conexion.conn.cursor()
                    cur.execute("INSERT INTO usuarios (nombre_completo, username, password, rol, curso_asignado) VALUES (%s, %s, %s, %s, %s)",
                                 (nombre_completo, username, password, rol, curso_asignado))
                    conexion.conn.commit()
                    cur.close()
                else:
                    conexion.execute("INSERT INTO usuarios (nombre_completo, username, password, rol, curso_asignado) VALUES (?, ?, ?, ?, ?)",
                                     (nombre_completo, username, password, rol, curso_asignado))
                    conexion.commit()
                flash('Maestro registrado.', 'success')
                
            return redirect(url_for('registrar_usuario'))
        
        # Obtener lista de maestros
        if is_postgres:
            cur = conexion.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM usuarios WHERE LOWER(rol) = 'maestro'")
            maestros = cur.fetchall()
            cur.close()
        else:
            conexion.row_factory = sqlite3.Row
            maestros = conexion.execute("SELECT * FROM usuarios WHERE LOWER(rol) = 'maestro'").fetchall()

    except Exception as e:
        print("--- ERROR EN REGISTRAR USUARIO:", e)
    finally:
        conexion.close()

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

import re
from flask import render_template, request, redirect, url_for, session, flash

@app.route('/registrar_expediente_viejo', methods=['GET', 'POST'])
def registrar_expediente_viejo():
    if 'usuario' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('menu'))

    conexion = get_db_connection()
    is_postgres = DATABASE_URL is not None
    ultimo_valor = None
    total_estudiantes = 0
    total_expedientes = 0
    total_usuarios = 0

    try:
        if is_postgres:
            cur = conexion.conn.cursor()
            
            # Intentamos obtener el último registro de la tabla expedientes_viejos
            try:
                cur.execute('SELECT "Unnamed: 5" FROM expedientes_viejos ORDER BY ctid DESC LIMIT 1')
                resultado = cur.fetchone()
                if resultado:
                    ultimo_valor = resultado[0]
            except Exception:
                pass

            # Totales seguros
            try:
                cur.execute('SELECT COUNT(*) FROM estudiantes')
                total_estudiantes = cur.fetchone()[0]
            except: pass

            try:
                cur.execute('SELECT COUNT(*) FROM expedientes_viejos')
                total_expedientes = cur.fetchone()[0]
            except: pass

            try:
                cur.execute('SELECT COUNT(*) FROM usuarios')
                total_usuarios = cur.fetchone()[0]
            except: pass
            
            cur.close()
        else:
            cursor = conexion.cursor()
            cursor.execute('SELECT "Unnamed: 5" FROM expedientes_viejos ORDER BY rowid DESC LIMIT 1')
            resultado = cursor.fetchone()
            if resultado:
                ultimo_valor = resultado[0]

            cursor.execute('SELECT COUNT(*) FROM estudiantes')
            total_estudiantes = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM expedientes_viejos')
            total_expedientes = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM usuarios')
            total_usuarios = cursor.fetchone()[0]
            
            cursor.close()
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        conexion.close()

    # Autoincremento basado en el último número real encontrado (ej. 500 -> 501)
    siguiente_ficha = "F-501" # Por si acaso está totalmente vacío
    if ultimo_valor:
        numeros = re.findall(r'\d+', str(ultimo_valor))
        if numeros:
            siguiente_numero = int(numeros[-1]) + 1
            siguiente_ficha = f"F-{siguiente_numero}"

    return render_template(
        'registrar_expediente_viejo.html', 
        siguiente_ficha=siguiente_ficha,
        total_estudiantes=total_estudiantes,
        total_expedientes=total_expedientes,
        total_usuarios=total_usuarios
    )

@app.route('/guardar_expediente_viejo', methods=['POST'])
def guardar_expediente_viejo():
    # Validar sesión y rol de administrador también al guardar
    if 'usuario' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado.', 'danger')
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