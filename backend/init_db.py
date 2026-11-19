from db import conectar

def inicializar_bd():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        legajo VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        prioridad ENUM('baja', 'media', 'alta') NOT NULL,
        categoria VARCHAR(150) NOT NULL,
        descripcion TEXT NOT NULL,
        estado ENUM('pendiente', 'solucionado') DEFAULT 'pendiente',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libros (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(255) NOT NULL,
        subtitulo VARCHAR(255) DEFAULT '',
        autor VARCHAR(255) NOT NULL,
        editorial VARCHAR(150) NOT NULL,
        anio INT NOT NULL,
        universidad ENUM('UTN', 'UCES', 'UFLO') NOT NULL,
        carrera VARCHAR(200) NOT NULL,
        nro_inventario VARCHAR(50) NOT NULL,
        disponible BOOLEAN DEFAULT TRUE,
        eliminado BOOLEAN DEFAULT FALSE,
        motivo_baja VARCHAR(255) DEFAULT NULL,
        fecha_baja DATETIME DEFAULT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM libros")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO libros (titulo, subtitulo, autor, editorial, anio, universidad, carrera, nro_inventario, disponible)
        VALUES 
        ('Ingeniería de Software: Un enfoque práctico', 'Séptima edición', 'Roger S. Pressman', 'McGraw-Hill', 2010, 'UTN', 'Ingeniería en Sistemas de Información', 'INV-003721', TRUE),
        ('Introducción a la Psicología Social', '', 'Serge Moscovici', 'Paidós', 2008, 'UCES', 'Licenciatura en Psicología', 'INV-004102', TRUE),
        ('Fisiología del Ejercicio', 'Nutrición, rendimiento y salud', 'William D. McArdle', 'Panamericana', 2015, 'UFLO', 'Licenciatura en Actividad Física y Deporte', 'INV-001890', FALSE)
        """)

    conexion.commit()
    cursor.close()
    conexion.close()
    print("¡Tablas creadas y datos iniciales cargados en Clever Cloud con éxito!")

if __name__ == "__main__":
    inicializar_bd()