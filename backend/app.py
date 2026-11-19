from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from db import conectar
except ImportError:
    from backend.db import conectar

app = Flask(__name__)
CORS(app)

_esquema_verificado = False
# ==========================================
# HELPERS DE FORMATEO Y ESQUEMA MYSQL
# ==========================================

def _formatear_fecha(valor):
    if not valor:
        return ''
    if hasattr(valor, 'strftime'):
        return valor.strftime('%d/%m/%Y %H:%M')
    return str(valor)


def _formatear_libro(row):
    return {
        'id': row['id'],
        'title': row['titulo'],
        'subtitle': row.get('subtitulo') or '',
        'author': row['autor'],
        'publisher': row['editorial'],
        'year': row['anio'],
        'library': row['universidad'],
        'career': row['carrera'],
        'inventoryNumber': row['nro_inventario'],
        'available': bool(row['disponible']),
        'deletedAt': _formatear_fecha(row.get('fecha_baja')),
        'deleteReason': row.get('motivo_baja') or 'Sin motivo especificado'
    }


def _asegurar_esquema(cursor):
    global _esquema_verificado
    if _esquema_verificado:
        return

    # 1. Tabla Tickets + columnas necesarias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL,
            legajo VARCHAR(50),
            email VARCHAR(120) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            prioridad VARCHAR(20) DEFAULT 'media',
            descripcion TEXT NOT NULL,
            estado VARCHAR(30) DEFAULT 'Pendiente',
            imagen_base64 LONGTEXT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SHOW COLUMNS FROM tickets LIKE 'estado'")
    col_estado = cursor.fetchone()
    if col_estado:
        col_type = col_estado['Type'] if isinstance(col_estado, dict) else col_estado[1]
        if isinstance(col_type, bytes):
            col_type = col_type.decode('utf-8')
        if 'varchar(30)' not in col_type.lower():
            cursor.execute("ALTER TABLE tickets MODIFY COLUMN estado VARCHAR(30) NOT NULL DEFAULT 'Pendiente'")
            cursor.execute("""
                UPDATE tickets
                SET estado = 'Pendiente'
                WHERE estado IS NULL OR estado = '' OR estado NOT IN ('Pendiente', 'En proceso', 'Solucionado')
            """)

    cursor.execute("SHOW COLUMNS FROM tickets LIKE 'imagen_base64'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE tickets ADD COLUMN imagen_base64 LONGTEXT NULL")

    # 2. Tabla Usuarios + Admin por defecto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL DEFAULT 'alumno',
            legajo VARCHAR(50),
            universidad VARCHAR(50) DEFAULT 'UTN',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", ('admin@utn.edu.ar',))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password_hash, rol, legajo, universidad)
            VALUES (%s, %s, %s, 'admin', 'ADMIN-01', 'UTN')
        """, ('Administrador Biblioteca', 'admin@utn.edu.ar', generate_password_hash('admin123')))

    # 3. Tabla Préstamos / Reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            libro_id INT NOT NULL,
            usuario_id INT NOT NULL,
            usuario_nombre VARCHAR(120) NOT NULL,
            usuario_rol VARCHAR(20) NOT NULL,
            usuario_legajo VARCHAR(50),
            usuario_email VARCHAR(120) NOT NULL,
            dias_prestamo INT NOT NULL DEFAULT 7,
            estado VARCHAR(30) NOT NULL DEFAULT 'Pendiente',
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_devolucion DATETIME NULL
        )
    """)

    _esquema_verificado = True


# ==========================================
# ENDPOINTS DE CATÁLOGO DE LIBROS
# ==========================================

@app.route('/api/libros', methods=['GET'])
def obtener_libros():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)
        cursor.execute("SELECT * FROM libros WHERE eliminado = FALSE ORDER BY id DESC")
        libros = [_formatear_libro(row) for row in cursor.fetchall()]
        return jsonify(libros)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/libros/bajas', methods=['GET'])
def obtener_libros_bajas():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM libros WHERE eliminado = TRUE ORDER BY fecha_baja DESC, id DESC")
        libros = [_formatear_libro(row) for row in cursor.fetchall()]
        return jsonify(libros)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/libros', methods=['POST'])
def agregar_libro():
    data = request.get_json() or {}
    titulo = data.get('title') or data.get('titulo') or ''
    subtitulo = data.get('subtitle') or data.get('subtitulo') or ''
    autor = data.get('author') or data.get('autor') or ''
    editorial = data.get('publisher') or data.get('editorial') or ''
    anio = data.get('year') or data.get('anio') or 2024
    universidad = data.get('library') or data.get('universidad') or 'UTN'
    carrera = data.get('career') or data.get('carrera') or ''
    nro_inventario = data.get('inventoryNumber') or data.get('nro_inventario') or ''
    disponible = data.get('available') if 'available' in data else data.get('disponible', True)

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO libros (
                titulo, subtitulo, autor, editorial, anio,
                universidad, carrera, nro_inventario, disponible, eliminado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
        """, (titulo, subtitulo, autor, editorial, anio, universidad, carrera, nro_inventario, bool(disponible)))
        conexion.commit()

        nuevo_id = cursor.lastrowid
        cursor.execute("SELECT * FROM libros WHERE id = %s", (nuevo_id,))
        nuevo_libro = _formatear_libro(cursor.fetchone())
        return jsonify(nuevo_libro), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/libros/<int:libro_id>', methods=['PUT'])
def actualizar_libro(libro_id):
    data = request.get_json() or {}
    titulo = data.get('title') or data.get('titulo') or ''
    subtitulo = data.get('subtitle') or data.get('subtitulo') or ''
    autor = data.get('author') or data.get('autor') or ''
    editorial = data.get('publisher') or data.get('editorial') or ''
    anio = data.get('year') or data.get('anio') or 2024
    universidad = data.get('library') or data.get('universidad') or 'UTN'
    carrera = data.get('career') or data.get('carrera') or ''
    nro_inventario = data.get('inventoryNumber') or data.get('nro_inventario') or ''
    disponible = data.get('available') if 'available' in data else data.get('disponible', True)

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            UPDATE libros
            SET titulo = %s, subtitulo = %s, autor = %s, editorial = %s, anio = %s,
                universidad = %s, carrera = %s, nro_inventario = %s, disponible = %s
            WHERE id = %s
        """, (titulo, subtitulo, autor, editorial, anio, universidad, carrera, nro_inventario, bool(disponible), libro_id))
        conexion.commit()

        cursor.execute("SELECT * FROM libros WHERE id = %s", (libro_id,))
        actualizado = _formatear_libro(cursor.fetchone())
        return jsonify(actualizado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/libros/<int:libro_id>/baja', methods=['POST'])
def dar_baja_libro(libro_id):
    data = request.get_json(silent=True) or {}
    motivo = (
        data.get('motivo')
        or data.get('reason')
        or data.get('deleteReason')
        or 'Baja administrativa'
    )

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            UPDATE libros
            SET eliminado = TRUE, motivo_baja = %s, fecha_baja = NOW()
            WHERE id = %s
        """, (motivo, libro_id))
        conexion.commit()

        cursor.execute("SELECT * FROM libros WHERE id = %s", (libro_id,))
        libro_baja = _formatear_libro(cursor.fetchone())
        return jsonify(libro_baja)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/libros/<int:libro_id>/restaurar', methods=['POST'])
def restaurar_libro(libro_id):
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            UPDATE libros
            SET eliminado = FALSE, motivo_baja = NULL, fecha_baja = NULL
            WHERE id = %s
        """, (libro_id,))
        conexion.commit()

        cursor.execute("SELECT * FROM libros WHERE id = %s", (libro_id,))
        libro_restaurado = _formatear_libro(cursor.fetchone())
        return jsonify(libro_restaurado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/libros/<int:libro_id>', methods=['DELETE'])
def eliminar_libro_definitivo(libro_id):
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM libros WHERE id = %s", (libro_id,))
        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ==========================================
# ENDPOINTS DE PRÉSTAMOS Y RESERVAS
# ==========================================

@app.route('/api/prestamos', methods=['GET'])
def obtener_prestamos():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)
        cursor.execute("""
            SELECT
                p.id, p.libro_id, p.usuario_id, p.usuario_nombre, p.usuario_rol,
                p.usuario_legajo, p.usuario_email, p.dias_prestamo, p.estado,
                DATE_FORMAT(p.fecha_solicitud, '%Y-%m-%dT%H:%i:%s') AS fecha_solicitud,
                DATE_FORMAT(p.fecha_devolucion, '%Y-%m-%dT%H:%i:%s') AS fecha_devolucion,
                l.titulo AS libro_titulo,
                l.autor AS libro_autor,
                l.nro_inventario AS libro_inventario,
                l.universidad AS libro_universidad
            FROM prestamos p
            LEFT JOIN libros l ON p.libro_id = l.id
            ORDER BY p.id DESC
        """)
        prestamos = cursor.fetchall()
        return jsonify({'success': True, 'prestamos': prestamos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/prestamos', methods=['POST'])
def solicitar_prestamo():
    data = request.get_json() or {}
    libro_id = data.get('libro_id')
    usuario_id = data.get('usuario_id')
    usuario_nombre = (data.get('usuario_nombre') or '').strip()
    usuario_rol = (data.get('usuario_rol') or 'alumno').strip().lower()
    usuario_legajo = (data.get('usuario_legajo') or '').strip()
    usuario_email = (data.get('usuario_email') or '').strip()

    if not libro_id or not usuario_id or not usuario_nombre:
        return jsonify({'success': False, 'error': 'Datos incompletos para solicitar préstamo.'}), 400

    # Profesores tienen 15 días de préstamo; Alumnos 7 días
    dias_prestamo = 15 if usuario_rol == 'profesor' else 7

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)

        cursor.execute("SELECT disponible, eliminado FROM libros WHERE id = %s", (libro_id,))
        libro = cursor.fetchone()
        if not libro or libro['eliminado'] or not libro['disponible']:
            return jsonify({'success': False, 'error': 'El ejemplar ya no se encuentra disponible.'}), 400

        cursor.execute("""
            SELECT id FROM prestamos
            WHERE libro_id = %s AND usuario_id = %s AND estado IN ('Pendiente', 'Aprobado')
        """, (libro_id, usuario_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Ya tenés una solicitud activa para este libro.'}), 409

        cursor.execute("""
            INSERT INTO prestamos (
                libro_id, usuario_id, usuario_nombre, usuario_rol,
                usuario_legajo, usuario_email, dias_prestamo, estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendiente')
        """, (libro_id, usuario_id, usuario_nombre, usuario_rol, usuario_legajo, usuario_email, dias_prestamo))
        conexion.commit()

        return jsonify({'success': True, 'id': cursor.lastrowid, 'dias_prestamo': dias_prestamo}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/prestamos/<int:prestamo_id>', methods=['PUT'])
def actualizar_estado_prestamo(prestamo_id):
    data = request.get_json() or {}
    nuevo_estado = (data.get('estado') or '').strip()
    if nuevo_estado not in ('Pendiente', 'Aprobado', 'Devuelto', 'Rechazado'):
        return jsonify({'success': False, 'error': 'Estado de préstamo no válido.'}), 400

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)

        cursor.execute("SELECT libro_id, estado FROM prestamos WHERE id = %s", (prestamo_id,))
        prestamo = cursor.fetchone()
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado.'}), 404

        if nuevo_estado == 'Devuelto':
            cursor.execute("""
                UPDATE prestamos SET estado = 'Devuelto', fecha_devolucion = NOW()
                WHERE id = %s
            """, (prestamo_id,))
            cursor.execute("UPDATE libros SET disponible = TRUE WHERE id = %s", (prestamo['libro_id'],))
        elif nuevo_estado == 'Aprobado':
            cursor.execute("UPDATE prestamos SET estado = 'Aprobado' WHERE id = %s", (prestamo_id,))
            cursor.execute("UPDATE libros SET disponible = FALSE WHERE id = %s", (prestamo['libro_id'],))
        else:
            cursor.execute("UPDATE prestamos SET estado = %s WHERE id = %s", (nuevo_estado, prestamo_id))
            if prestamo['estado'] == 'Aprobado':
                cursor.execute("UPDATE libros SET disponible = TRUE WHERE id = %s", (prestamo['libro_id'],))

        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/prestamos/<int:prestamo_id>', methods=['DELETE'])
def eliminar_prestamo(prestamo_id):
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT libro_id, estado FROM prestamos WHERE id = %s", (prestamo_id,))
        prestamo = cursor.fetchone()
        if prestamo and prestamo['estado'] == 'Aprobado':
            cursor.execute("UPDATE libros SET disponible = TRUE WHERE id = %s", (prestamo['libro_id'],))

        cursor.execute("DELETE FROM prestamos WHERE id = %s", (prestamo_id,))
        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ==========================================
# ENDPOINTS DE TICKETS DE SOPORTE
# ==========================================

@app.route('/api/tickets', methods=['GET'])
def obtener_tickets():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)
        cursor.execute("""
            SELECT
                id, nombre, legajo, email, categoria, prioridad,
                descripcion, estado, imagen_base64,
                DATE_FORMAT(fecha_creacion, '%Y-%m-%dT%H:%i:%s') AS fecha_creacion
            FROM tickets
            ORDER BY id DESC
        """)
        tickets = cursor.fetchall()
        return jsonify({'success': True, 'tickets': tickets})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    legajo = (data.get('legajo') or '').strip()
    email = (data.get('email') or '').strip()
    categoria = (data.get('categoria') or '').strip()
    prioridad = (data.get('prioridad') or 'media').strip().lower()
    descripcion = (data.get('descripcion') or '').strip()
    imagen_base64 = data.get('imagen_base64') or None

    if not nombre or not email or not categoria or not descripcion:
        return jsonify({'success': False, 'error': 'Faltan campos obligatorios.'}), 400

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        _asegurar_esquema(cursor)
        cursor.execute("""
            INSERT INTO tickets (
                nombre, legajo, email, categoria, prioridad,
                descripcion, estado, imagen_base64
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente', %s)
        """, (nombre, legajo, email, categoria, prioridad, descripcion, imagen_base64))
        conexion.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
def actualizar_estado_ticket(ticket_id):
    data = request.get_json() or {}
    nuevo_estado = (data.get('estado') or '').strip()
    if nuevo_estado not in ('Pendiente', 'En proceso', 'Solucionado'):
        return jsonify({'success': False, 'error': 'Estado no válido.'}), 400

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        _asegurar_esquema(cursor)
        cursor.execute("UPDATE tickets SET estado = %s WHERE id = %s", (nuevo_estado, ticket_id))
        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def eliminar_ticket(ticket_id):
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ==========================================
# ENDPOINTS DE USUARIOS (AUTH + GESTIÓN ADMIN)
# ==========================================

@app.route('/api/auth/registro', methods=['POST'])
def registrar_usuario():
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    rol = (data.get('rol') or 'alumno').strip().lower()
    legajo = (data.get('legajo') or '').strip()
    universidad = (data.get('universidad') or 'UTN').strip().upper()

    if rol not in ('alumno', 'profesor'):
        rol = 'alumno'

    if not nombre or not email or not password or not legajo:
        return jsonify({'success': False, 'error': 'Completá todos los campos obligatorios.'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres.'}), 400

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)

        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Ya existe una cuenta registrada con ese correo.'}), 409

        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password_hash, rol, legajo, universidad)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, email, password_hash, rol, legajo, universidad))
        conexion.commit()

        nuevo_id = cursor.lastrowid
        return jsonify({
            'success': True,
            'user': {
                'id': nuevo_id,
                'nombre': nombre,
                'email': email,
                'rol': rol,
                'legajo': legajo,
                'universidad': universidad
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/auth/login', methods=['POST'])
def login_usuario():
    data = request.get_json() or {}
    email_input = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email_input or not password:
        return jsonify({'success': False, 'error': 'Ingresá tu correo y contraseña.'}), 400

    email_busqueda = 'admin@utn.edu.ar' if email_input == 'admin' else email_input

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)

        cursor.execute("""
            SELECT id, nombre, email, password_hash, rol, legajo, universidad
            FROM usuarios
            WHERE email = %s
        """, (email_busqueda,))
        usuario = cursor.fetchone()

        if not usuario or not check_password_hash(usuario['password_hash'], password):
            return jsonify({'success': False, 'error': 'Correo o contraseña incorrectos.'}), 401

        return jsonify({
            'success': True,
            'user': {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'email': usuario['email'],
                'rol': usuario['rol'],
                'legajo': usuario['legajo'],
                'universidad': usuario['universidad']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        _asegurar_esquema(cursor)
        cursor.execute("""
            SELECT
                id, nombre, email, rol, legajo, universidad,
                DATE_FORMAT(fecha_registro, '%Y-%m-%dT%H:%i:%s') AS fecha_registro
            FROM usuarios
            ORDER BY id DESC
        """)
        usuarios = cursor.fetchall()
        return jsonify({'success': True, 'usuarios': usuarios})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/usuarios/<int:usuario_id>/rol', methods=['PUT'])
def cambiar_rol_usuario(usuario_id):
    data = request.get_json() or {}
    nuevo_rol = (data.get('rol') or '').strip().lower()
    if nuevo_rol not in ('alumno', 'profesor', 'admin'):
        return jsonify({'success': False, 'error': 'Rol no válido.'}), 400

    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT email FROM usuarios WHERE id = %s", (usuario_id,))
        u = cursor.fetchone()
        if not u:
            return jsonify({'success': False, 'error': 'Usuario no encontrado.'}), 404
        if u['email'] == 'admin@utn.edu.ar' and nuevo_rol != 'admin':
            return jsonify({'success': False, 'error': 'No se puede quitar el rol al administrador principal.'}), 403

        cursor.execute("UPDATE usuarios SET rol = %s WHERE id = %s", (nuevo_rol, usuario_id))
        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT email FROM usuarios WHERE id = %s", (usuario_id,))
        u = cursor.fetchone()
        if not u:
            return jsonify({'success': False, 'error': 'Usuario no encontrado.'}), 404
        if u['email'] == 'admin@utn.edu.ar':
            return jsonify({'success': False, 'error': 'No se puede eliminar al administrador principal.'}), 403

        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)