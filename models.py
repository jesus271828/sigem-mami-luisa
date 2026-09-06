from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Instancia única de SQLAlchemy para todo el proyecto
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
    numero_orden = db.Column(db.String(10), nullable=True)


# Modelo para la Planificación
class Planificacion(db.Model):
    __tablename__ = 'planificacion'
    id = db.Column(db.Integer, primary_key=True)
    docente = db.Column(db.String(100), nullable=False)
    grado = db.Column(db.String(50), nullable=False)
    areas = db.Column(db.String(255))
    modalidad = db.Column(db.String(50))
    situacion = db.Column(db.Text)
    competencias = db.Column(db.Text)
    contenidos = db.Column(db.Text)
    actividades = db.Column(db.Text)
    indicadores = db.Column(db.Text)
    recursos = db.Column(db.Text)
    evaluacion = db.Column(db.Text)
    valor = db.Column(db.String(100))
    efemerides = db.Column(db.Text)
    duracion = db.Column(db.Integer)
    f_inicio = db.Column(db.String(20))
    f_cierre = db.Column(db.String(20))


# Modelo para la tabla notas1
class Notas1(db.Model):
    __tablename__ = 'notas1'
    
    id = db.Column(db.Integer, primary_key=True)
    id_estudiante = db.Column(db.String(50), unique=True, nullable=False)
    datos_formulario = db.Column(db.Text, nullable=True)


# Modelo para la tabla notas2 (Guardado eficiente en formato JSON)
class Notas2(db.Model):
    __tablename__ = 'notas2'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False, unique=True)
    datos_formulario = db.Column(db.Text, nullable=True) # Guarda todo el diccionario de los inputs del formulario

class Asistencia(db.Model):
    __tablename__ = 'asistencia'
    
    id = db.Column('identificación', db.Integer, primary_key=True)
    id_estudiante = db.Column(db.Integer, nullable=False)
    grado = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False) # 'Presente', 'Ausente', 'Tarde'


class RegistroPersonal(db.Model):
    __tablename__ = 'asistencia_personal'

    id = db.Column(db.Integer, primary_key=True)  # O id_registro, pero sin tildes ni eñes en la base de datos
    fecha = db.Column(db.String(20), unique=True)
    adm_presente = db.Column(db.Integer, default=0)
    adm_ausentes = db.Column(db.String(255), nullable=True)
    aux_presente = db.Column(db.Integer, default=0)
    aux_ausentes = db.Column(db.String(255), nullable=True)
    doc_presente = db.Column(db.Integer, default=0)
    doc_ausentes = db.Column(db.String(255), nullable=True)