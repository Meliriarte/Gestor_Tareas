from db import get_connection
from psycopg2.extras import RealDictCursor


class Usuario:
    @staticmethod
    def crear(nombre, usuario, contraseña):
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO usuarios (nombre, usuario, contraseña)
                    VALUES (%s, %s, %s)
                    RETURNING id, nombre, usuario
                    """,
                    (nombre, usuario, contraseña),
                )
                resultado = cur.fetchone()
            conn.commit()
            return dict(resultado)
        except Exception as e:
            conn.rollback()
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise ValueError("El usuario ya existe.")
            raise e
        finally:
            conn.close()

    @staticmethod
    def buscar_por_usuario(usuario):
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, nombre, usuario, contraseña FROM usuarios WHERE usuario = %s",
                    (usuario,),
                )
                resultado = cur.fetchone()
            return dict(resultado) if resultado else None
        finally:
            conn.close()

    @staticmethod
    def buscar_por_id(usuario_id):
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, nombre, usuario FROM usuarios WHERE id = %s",
                    (usuario_id,),
                )
                resultado = cur.fetchone()
            return dict(resultado) if resultado else None
        finally:
            conn.close()


class Tarea:
    @staticmethod
    def obtener_tareas(usuario_id):
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, texto, completada, fecha_limite
                    FROM tareas
                    WHERE usuario_id = %s
                    ORDER BY
                        CASE WHEN fecha_limite IS NULL THEN 1 ELSE 0 END,
                        fecha_limite ASC,
                        id ASC
                    """,
                    (usuario_id,),
                )
                tareas = cur.fetchall()
            return [dict(t) for t in tareas]
        finally:
            conn.close()

    @staticmethod
    def agregar(usuario_id, texto, fecha_limite=None):
        texto_limpio = texto.strip()
        if not texto_limpio:
            raise ValueError("La tarea no puede estar vacía.")

        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO tareas (usuario_id, texto, completada, fecha_limite)
                    VALUES (%s, %s, FALSE, %s)
                    RETURNING id, texto, completada, fecha_limite
                    """,
                    (usuario_id, texto_limpio, fecha_limite),
                )
                tarea = dict(cur.fetchone())
            conn.commit()
            return tarea
        finally:
            conn.close()

    @staticmethod
    def editar(tarea_id, usuario_id, nuevo_texto, fecha_limite=None):
        texto_limpio = nuevo_texto.strip()
        if not texto_limpio:
            raise ValueError("La tarea no puede estar vacía.")

        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE tareas
                    SET texto = %s, fecha_limite = %s
                    WHERE id = %s AND usuario_id = %s
                    RETURNING id, texto, completada, fecha_limite
                    """,
                    (texto_limpio, fecha_limite, tarea_id, usuario_id),
                )
                resultado = cur.fetchone()
            if not resultado:
                conn.rollback()
                raise LookupError("La tarea no existe.")
            conn.commit()
            return dict(resultado)
        finally:
            conn.close()

    @staticmethod
    def cambiar_estado(tarea_id, usuario_id, completada):
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE tareas
                    SET completada = %s
                    WHERE id = %s AND usuario_id = %s
                    RETURNING id, texto, completada, fecha_limite
                    """,
                    (bool(completada), tarea_id, usuario_id),
                )
                resultado = cur.fetchone()
            if not resultado:
                conn.rollback()
                raise LookupError("La tarea no existe.")
            conn.commit()
            return dict(resultado)
        finally:
            conn.close()

    @staticmethod
    def eliminar(tarea_id, usuario_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tareas WHERE id = %s AND usuario_id = %s RETURNING id",
                    (tarea_id, usuario_id),
                )
                if not cur.fetchone():
                    conn.rollback()
                    raise LookupError("La tarea no existe.")
            conn.commit()
        finally:
            conn.close()
