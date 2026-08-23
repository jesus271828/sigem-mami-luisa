from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Modelo para los usuarios (Docentes y Oficina)
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'docente' o 'oficina'
    grado_asignado = db.Column(db.String(50), nullable=True) # Para el autocompletado


class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    grado = db.Column(db.String(50), nullable=False)
    numero_orden = db.Column(db.String(10), nullable=True) # <-- Coincide con tu base de datos


# Modelo para la Planificación
class Planificacion(db.Model):
    __tablename__ = 'planificacion'
    id = db.Column(db.Integer, primary_key=True)
    # Identificación
    docente = db.Column(db.String(100), nullable=False)
    grado = db.Column(db.String(50), nullable=False)
    # Áreas y Estrategias
    areas = db.Column(db.String(255))
    modalidad = db.Column(db.String(50))
    # Contenido Pedagógico
    situacion = db.Column(db.Text)
    competencias = db.Column(db.Text)
    contenidos = db.Column(db.Text)
    actividades = db.Column(db.Text)
    # Detalles
    indicadores = db.Column(db.Text)
    recursos = db.Column(db.Text)
    evaluacion = db.Column(db.Text)
    valor = db.Column(db.String(100))
    efemerides = db.Column(db.Text)
    duracion = db.Column(db.Integer)
    f_inicio = db.Column(db.String(20))
    f_cierre = db.Column(db.String(20))


# Modelo para la tabla notas1 (un registro único por estudiante para evitar duplicados)
class Notas1(db.Model):
    __tablename__ = 'notas1'
    
    id = db.Column(db.Integer, primary_key=True)
    id_estudiante = db.Column(db.String(50), unique=True, nullable=False)  # Llave única por estudiante
    datos_formulario = db.Column(db.Text, nullable=True)  # Almacena los campos del formulario en formato JSON

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Nota2(db.Model):
    __tablename__ = 'nota2'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False, unique=True)
    # Aquí guardaremos toda la estructura de notas en formato JSON
    # Ejemplo: {"Matemáticas": {"p1": 90, "p2": 85}, "Español": {"p1": 88, "p2": 92}}
    datos_notas = db.Column(db.JSON, nullable=False, default=dict)