import sqlite3

def crear_tablas():
    conexion = sqlite3.connect('sigem_ml.db')
    cursor = conexion.cursor()

    print("Creando las tres tablas con los campos exactos del código...")

    # Borramos las tablas anteriores para aplicar la nueva estructura exacta
    cursor.execute('DROP TABLE IF EXISTS inscripciones')
    cursor.execute('DROP TABLE IF EXISTS estudiantes')
    cursor.execute('DROP TABLE IF EXISTS autorizados')

    # 1. TABLA INSCRIPCIONES (Formulario completo histórico)
    cursor.execute('''
        CREATE TABLE inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anio_escolar TEXT, fecha_inscripcion TEXT, id_estudiante TEXT, nombres TEXT, apellidos TEXT,
            grado TEXT, fecha_nacimiento TEXT, edad TEXT, sexo TEXT, nacionalidad TEXT, lugar_nac TEXT,
            direccion TEXT, cant_hermanos TEXT, edades_hermanos TEXT, lugar_ocupa TEXT, tipo_sangre TEXT,
            seguro_medico TEXT, foto_estudiante_cedula TEXT, alergias TEXT, medicamentos TEXT,
            medico_pediatra TEXT, centro_medico TEXT, emergencia_tel TEXT, emergencia_nombre TEXT,
            emergencia_parentesco TEXT, padre_nombre TEXT, padre_sector TEXT, padre_direccion TEXT,
            padre_profesion TEXT, padre_cedula TEXT, foto_padre_cedula TEXT, padre_nivel TEXT,
            padre_religion TEXT, padre_tel_personal TEXT, padre_tel_trabajo TEXT, padre_correo TEXT,
            madre_nombre TEXT, madre_sector TEXT, madre_direccion TEXT, madre_profesion TEXT,
            madre_cedula TEXT, foto_madre_cedula TEXT, madre_nivel TEXT, madre_religion TEXT,
            madre_tel_personal TEXT, madre_tel_trabajo TEXT, madre_correo TEXT, tutor_nombre TEXT,
            tutor_sector TEXT, tutor_direccion TEXT, tutor_profesion TEXT, tutor_cedula TEXT,
            foto_tutor_cedula TEXT, tutor_nivel TEXT, tutor_religion TEXT, tutor_tel_personal TEXT,
            tutor_tel_trabajo TEXT, tutor_correo TEXT, vive_nombres TEXT, vive_parentesco TEXT,
            vive_cedula TEXT, foto_vive_cedula TEXT, vive_direccion TEXT, vive_sector TEXT,
            vive_profesion TEXT, vive_nivel TEXT, vive_religion TEXT, vive_tel_personal TEXT,
            vive_tel_trabajo TEXT, vive_correo TEXT, econ_nombres TEXT, econ_parentesco TEXT,
            econ_cedula TEXT, foto_econ_cedula TEXT, econ_direccion TEXT, econ_sector TEXT,
            econ_profesion TEXT, econ_lugar_trabajo TEXT, econ_tel_personal TEXT, econ_tel_trabajo TEXT,
            econ_correo TEXT, aut_nombre_1 TEXT, aut_cedula_1 TEXT, aut_parentesco_1 TEXT, aut_tel_1 TEXT,
            foto_aut_cedula_1 TEXT, aut_nombre_2 TEXT, aut_cedula_2 TEXT, aut_parentesco_2 TEXT, aut_tel_2 TEXT,
            foto_aut_cedula_2 TEXT, aut_nombre_3 TEXT, aut_cedula_3 TEXT, aut_parentesco_3 TEXT, aut_tel_3 TEXT,
            foto_aut_cedula_3 TEXT, aut_nombre_4 TEXT, aut_cedula_4 TEXT, aut_parentesco_4 TEXT, aut_tel_4 TEXT,
            foto_aut_cedula_4 TEXT, aut_nombre_5 TEXT, aut_cedula_5 TEXT, aut_parentesco_5 TEXT, aut_tel_5 TEXT,
            foto_aut_cedula_5 TEXT, autoriza_medicamentos TEXT, autoriza_redes TEXT, firma_redes TEXT
        )
    ''')

    # 2. TABLA ESTUDIANTES (Datos básicos y número de orden)
    cursor.execute('''
        CREATE TABLE estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT,
            apellidos TEXT,
            id_estudiante TEXT,
            grado TEXT,
            foto_estudiante_cedula TEXT,
            numero_orden INTEGER
        )
    ''')

    # 3. TABLA AUTORIZADOS (Exactamente los campos que tu código inserta en esta tabla)
    cursor.execute('''
        CREATE TABLE autorizados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_estudiante TEXT,
            nombres TEXT,
            apellidos TEXT,
            grado TEXT,
            foto_estudiante_cedula TEXT,
            padre_nombre TEXT,
            padre_cedula TEXT,
            foto_padre_cedula TEXT,
            padre_tel_personal TEXT,
            padre_tel_trabajo TEXT,
            madre_nombre TEXT,
            madre_cedula TEXT,
            foto_madre_cedula TEXT,
            madre_tel_personal TEXT,
            madre_tel_trabajo TEXT,
            tutor_nombre TEXT,
            tutor_cedula TEXT,
            foto_tutor_cedula TEXT,
            tutor_tel_personal TEXT,
            tutor_tel_trabajo TEXT,
            aut_nombre_1 TEXT,
            aut_cedula_1 TEXT,
            aut_parentesco_1 TEXT,
            aut_tel_1 TEXT,
            foto_aut_cedula_1 TEXT,
            aut_nombre_2 TEXT,
            aut_cedula_2 TEXT,
            aut_parentesco_2 TEXT,
            aut_tel_2 TEXT,
            foto_aut_cedula_2 TEXT,
            aut_nombre_3 TEXT,
            aut_cedula_3 TEXT,
            aut_parentesco_3 TEXT,
            aut_tel_3 TEXT,
            foto_aut_cedula_3 TEXT,
            aut_nombre_4 TEXT,
            aut_cedula_4 TEXT,
            aut_parentesco_4 TEXT,
            aut_tel_4 TEXT,
            foto_aut_cedula_4 TEXT,
            aut_nombre_5 TEXT,
            aut_cedula_5 TEXT,
            aut_parentesco_5 TEXT,
            aut_tel_5 TEXT,
            foto_aut_cedula_5 TEXT
        )
    ''')

    conexion.commit()
    conexion.close()
    print("¡Tablas creadas con los campos exactos de tu código!")

if __name__ == '__main__':
    crear_tablas()