import sqlite3

def recrear_base_de_datos():
    # Conecta a tu archivo SQLite existente
    conexion = sqlite3.connect('sigem_ml.db')
    cursor = conexion.cursor()

    # 1. Eliminar la tabla vieja para evitar conflictos
    cursor.execute('DROP TABLE IF EXISTS inscripciones;')
    print("Tabla anterior eliminada correctamente.")

    # 2. Crear la nueva tabla con TODOS los campos
    cursor.execute('''
        CREATE TABLE inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Encabezado
            anio_escolar TEXT NOT NULL,
            fecha_inscripcion TEXT NOT NULL,
            
            -- 1. Datos del Estudiante
            id_estudiante TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            grado TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            edad INTEGER,
            sexo TEXT,
            nacionalidad TEXT,
            lugar_nac TEXT,
            direccion TEXT,
            cant_hermanos INTEGER,
            edades_hermanos TEXT,
            lugar_ocupa TEXT,
            tipo_sangre TEXT,
            seguro_medico TEXT,
            foto_estudiante_cedula TEXT,
            alergias TEXT,
            medicamentos TEXT,
            medico_pediatra TEXT,
            centro_medico TEXT,
            emergencia_tel TEXT,
            emergencia_nombre TEXT,
            emergencia_parentesco TEXT,

            -- 2. Datos del Padre
            padre_nombre TEXT,
            padre_sector TEXT,
            padre_direccion TEXT,
            padre_profesion TEXT,
            padre_cedula TEXT,
            foto_padre_cedula TEXT,
            padre_nivel TEXT,
            padre_religion TEXT,
            padre_tel_personal TEXT,
            padre_tel_trabajo TEXT,
            padre_correo TEXT,

            -- 2. Datos de la Madre
            madre_nombre TEXT,
            madre_sector TEXT,
            madre_direccion TEXT,
            madre_profesion TEXT,
            madre_cedula TEXT,
            foto_madre_cedula TEXT,
            madre_nivel TEXT,
            madre_religion TEXT,
            madre_tel_personal TEXT,
            madre_tel_trabajo TEXT,
            madre_correo TEXT,

            -- 2. Datos del Tutor
            tutor_nombre TEXT,
            tutor_sector TEXT,
            tutor_direccion TEXT,
            tutor_profesion TEXT,
            tutor_cedula TEXT,
            foto_tutor_cedula TEXT,
            tutor_nivel TEXT,
            tutor_religion TEXT,
            tutor_tel_personal TEXT,
            tutor_tel_trabajo TEXT,
            tutor_correo TEXT,

            -- 3. Persona con la que vive
            vive_nombres TEXT,
            vive_parentesco TEXT,
            vive_cedula TEXT,
            foto_vive_cedula TEXT,
            vive_direccion TEXT,
            vive_sector TEXT,
            vive_profesion TEXT,
            vive_nivel TEXT,
            vive_religion TEXT,
            vive_tel_personal TEXT,
            vive_tel_trabajo TEXT,
            vive_correo TEXT,

            -- 4. Principal Responsable Económico
            econ_nombres TEXT,
            econ_parentesco TEXT,
            econ_cedula TEXT,
            foto_econ_cedula TEXT,
            econ_direccion TEXT,
            econ_sector TEXT,
            econ_profesion TEXT,
            econ_lugar_trabajo TEXT,
            econ_tel_personal TEXT,
            econ_tel_trabajo TEXT,
            econ_correo TEXT,

            -- 5. Autorizados a Retirar (Del 1 al 5)
            aut_nombre_1 TEXT, aut_cedula_1 TEXT, aut_parentesco_1 TEXT, aut_tel_1 TEXT, foto_aut_cedula_1 TEXT,
            aut_nombre_2 TEXT, aut_cedula_2 TEXT, aut_parentesco_2 TEXT, aut_tel_2 TEXT, foto_aut_cedula_2 TEXT,
            aut_nombre_3 TEXT, aut_cedula_3 TEXT, aut_parentesco_3 TEXT, aut_tel_3 TEXT, foto_aut_cedula_3 TEXT,
            aut_nombre_4 TEXT, aut_cedula_4 TEXT, aut_parentesco_4 TEXT, aut_tel_4 TEXT, foto_aut_cedula_4 TEXT,
            aut_nombre_5 TEXT, aut_cedula_5 TEXT, aut_parentesco_5 TEXT, aut_tel_5 TEXT, foto_aut_cedula_5 TEXT,

            -- 6 y 7. Autorizaciones especiales
            autoriza_medicamentos TEXT DEFAULT 'NO',
            autoriza_redes TEXT DEFAULT 'NO',
            firma_redes TEXT,
            
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    conexion.commit()
    conexion.close()
    print("¡Nueva tabla 'inscripciones' creada con éxito y con todos los campos!")

if __name__ == '__main__':
    recrear_base_de_datos()