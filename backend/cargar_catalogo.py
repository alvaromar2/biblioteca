from db import conectar

CATALOGO_REAL = [
    # UTN - Ingeniería en Sistemas de Información
    ("Ingeniería de Software: Un enfoque práctico", "Séptima edición", "Roger S. Pressman", "McGraw-Hill", 2010, "UTN", "Ingeniería en Sistemas de Información", "UTN-SIS-001", True),
    ("Sistemas Operativos Modernos", "Tercera edición", "Andrew S. Tanenbaum", "Pearson Educación", 2009, "UTN", "Ingeniería en Sistemas de Información", "UTN-SIS-002", True),
    ("Redes de Computadoras", "Quinta edición", "Andrew S. Tanenbaum, David J. Wetherall", "Pearson Educación", 2012, "UTN", "Ingeniería en Sistemas de Información", "UTN-SIS-003", False),
    ("Fundamentos de Bases de Datos", "Sexta edición", "Abraham Silberschatz, Henry F. Korth", "McGraw-Hill", 2014, "UTN", "Ingeniería en Sistemas de Información", "UTN-SIS-004", True),
    ("Introduction to Algorithms", "Third Edition", "Thomas H. Cormen, Charles E. Leiserson", "MIT Press", 2009, "UTN", "Ingeniería en Sistemas de Información", "UTN-SIS-005", True),

    # UTN - Tecnicatura Universitaria en Programación
    ("Cómo programar en C/C++ y Java", "Novena edición", "Paul Deitel, Harvey Deitel", "Pearson Educación", 2014, "UTN", "Tecnicatura Universitaria en Programación", "UTN-PRG-001", True),
    ("Código Limpio (Clean Code)", "Manual de estilo para el desarrollo ágil de software", "Robert C. Martin", "Anaya Multimedia", 2012, "UTN", "Tecnicatura Universitaria en Programación", "UTN-PRG-002", False),

    # UTN - Electromecánica, Electrónica e Industrial
    ("Cálculo de una variable: Trascendentes tempranas", "Octava edición", "James Stewart", "Cengage Learning", 2018, "UTN", "Ingeniería Electromecánica", "UTN-ELM-001", True),
    ("Física Universitaria con Física Moderna", "Volumen 1 - Decimocuarta edición", "Hugh D. Young, Roger A. Freedman (Sears-Zemansky)", "Pearson Educación", 2018, "UTN", "Ingeniería Electromecánica", "UTN-ELM-002", True),
    ("Ingeniería Mecánica: Estática", "Decimocuarta edición", "Russell C. Hibbeler", "Pearson Educación", 2016, "UTN", "Ingeniería Electromecánica", "UTN-ELM-003", False),
    ("Máquinas Eléctricas", "Quinta edición", "Stephen J. Chapman", "McGraw-Hill", 2012, "UTN", "Ingeniería Electromecánica", "UTN-ELM-004", True),
    ("Electrónica: Teoría de Circuitos y Dispositivos Electrónicos", "Décima edición", "Robert L. Boylestad, Louis Nashelsky", "Pearson Educación", 2009, "UTN", "Ingeniería Electrónica", "UTN-ELC-001", True),
    ("Álgebra Lineal y sus Aplicaciones", "Quinta edición", "David C. Lay, Steven R. Lay", "Pearson Educación", 2016, "UTN", "Ingeniería Electrónica", "UTN-ELC-002", True),
    ("Ingeniería Industrial: Métodos, estándares y diseño del trabajo", "Decimosegunda edición", "Benjamin W. Niebel, Andris Freivalds", "McGraw-Hill", 2009, "UTN", "Ingeniería Industrial (Convenio CRES San Francisco)", "UTN-IND-001", True),

    # UTN - Ingeniería Química y Administración Rural
    ("Química", "Decimosegunda edición", "Raymond Chang, Kenneth A. Goldsby", "McGraw-Hill", 2017, "UTN", "Ingeniería Química", "UTN-QUI-001", True),
    ("Principios Elementales de los Procesos Químicos", "Tercera edición", "Richard M. Felder, Ronald W. Rousseau", "Limusa Wiley", 2004, "UTN", "Ingeniería Química", "UTN-QUI-002", True),
    ("Manual del Ingeniero Químico", "Séptima edición (Tomo I)", "Robert H. Perry, Don W. Green", "McGraw-Hill", 2001, "UTN", "Ingeniería Química", "UTN-QUI-003", False),
    ("Administración", "Decimotercera edición", "Stephen P. Robbins, Mary Coulter", "Pearson Educación", 2018, "UTN", "Licenciatura en Administración Rural", "UTN-ADM-001", True),

    # UTN - Posgrados
    ("Data Mining: Practical Machine Learning Tools and Techniques", "Fourth Edition", "Ian H. Witten, Eibe Frank, Mark A. Hall", "Morgan Kaufmann", 2016, "UTN", "Maestría en Minería de Datos", "UTN-POS-001", True),
    ("Seguridad e Higiene en el Trabajo", "Enfoque integral", "César Ramírez Cavassa", "Limusa", 2013, "UTN", "Especialización en Higiene y Seguridad en el Trabajo", "UTN-POS-002", True),

    # UCES - Sede San Francisco
    ("Introducción a la Psicología Social", "Edición revisada", "Serge Moscovici", "Paidós", 2008, "UCES", "Licenciatura en Psicología", "UCES-PSI-001", True),
    ("Manual de Derecho Constitucional", "Segunda edición actualizada", "Néstor Pedro Sagüés", "Astrea", 2014, "UCES", "Abogacía", "UCES-ABO-001", True),
    ("Contabilidad Básica", "Sexta edición", "Enrique Fowler Newton", "La Ley", 2019, "UCES", "Contador Público", "UCES-CON-001", False),
    ("Administración de Recursos Humanos", "El capital humano de las organizaciones (Décima edición)", "Idalberto Chiavenato", "McGraw-Hill", 2017, "UCES", "Licenciatura en Recursos Humanos", "UCES-RRH-001", True),
    ("Dirección de Marketing", "Decimoquinta edición", "Philip Kotler, Kevin Lane Keller", "Pearson Educación", 2016, "UCES", "Licenciatura en Marketing", "UCES-MKT-001", True),
    ("Estrategia Competitiva", "Técnicas para el análisis de los sectores industriales y de la competencia", "Michael E. Porter", "Pirámide", 2015, "UCES", "Licenciatura en Dirección de Negocios", "UCES-NEG-001", True),

    # UFLO - Sede San Francisco
    ("Fisiología del Ejercicio", "Nutrición, rendimiento y salud", "William D. McArdle, Frank I. Katch", "Editorial Médica Panamericana", 2015, "UFLO", "Licenciatura en Actividad Física y Deporte", "UFLO-AFD-001", True),
    ("Las drogas: cerebro y sociedad", "Prevención y abordaje integral de los consumos problemáticos", "Carlos Damin", "Paidós", 2018, "UFLO", "Tecnicatura en Prevención en Drogadicción", "UFLO-TPD-001", True),
]


def cargar_catalogo():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM libros 
        WHERE nro_inventario IN (
            'INV-003721', 'INV-004102', 'INV-001890', 
            'UFLO-PSP-001', 'UFLO-NUT-001', 'UTN-SIS-006'
        )
    """)

    sql_check = "SELECT COUNT(*) FROM libros WHERE nro_inventario = %s"
    sql_insert = """
        INSERT INTO libros (
            titulo, subtitulo, autor, editorial, anio,
            universidad, carrera, nro_inventario, disponible
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    insertados = 0
    for libro in CATALOGO_REAL:
        cursor.execute(sql_check, (libro[7],))
        if cursor.fetchone()[0] == 0:
            cursor.execute(sql_insert, libro)
            insertados += 1

    cursor.execute("SELECT COUNT(*) FROM libros WHERE eliminado = FALSE")
    total_activos = cursor.fetchone()[0]

    conexion.commit()
    cursor.close()
    conexion.close()
    print(f"Nuevos libros agregados: {insertados}. Total activos en Clever Cloud: {total_activos}.")


if __name__ == "__main__":
    cargar_catalogo()