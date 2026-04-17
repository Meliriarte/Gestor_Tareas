import psycopg2
from psycopg2.extras import RealDictCursor
import os


class GestorTareas:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("La variable DATABASE_URL no esta configurada.")

    def _get_connection(self):
        return psycopg2.connect(self.database_url, sslmode="require")

    def _crear_tabla_si_no_existe(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tareas (
                    id SERIAL PRIMARY KEY,
                    texto VARCHAR(500) NOT NULL,
                    completada BOOLEAN DEFAULT FALSE,
                    fecha_limite TIMESTAMP NULL
                )
            """)
        conn.commit()

    def _leer_tareas_crudas(self):
        conn = self._get_connection()
        try:
            self._crear_tabla_si_no_existe(conn)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, texto, completada, fecha_limite
                    FROM tareas
                    ORDER BY
                        CASE WHEN fecha_limite IS NULL THEN 1 ELSE 0 END,
                        fecha_limite ASC,
                        id ASC
                """)
                tareas = cur.fetchall()
                return [dict(t) for t in tareas]
        finally:
            conn.close()

    def _siguiente_id(self, conn):
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM tareas")
            return cur.fetchone()[0]

    def obtener_tareas(self):
        return self._leer_tareas_crudas()

    def agregar_tarea(self, texto, fecha_limite=None):
        texto_limpio = texto.strip()
        if not texto_limpio:
            raise ValueError("La tarea no puede estar vacia.")

        conn = self._get_connection()
        try:
            self._crear_tabla_si_no_existe(conn)
            nuevo_id = self._siguiente_id(conn)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO tareas (id, texto, completada, fecha_limite)
                    VALUES (%s, %s, FALSE, %s)
                    RETURNING id, texto, completada, fecha_limite
                """,
                    (nuevo_id, texto_limpio, fecha_limite),
                )
                tarea = dict(cur.fetchone())
            conn.commit()
            return tarea
        finally:
            conn.close()

    def editar_tarea(self, tarea_id, nuevo_texto, fecha_limite=None):
        texto_limpio = nuevo_texto.strip()
        if not texto_limpio:
            raise ValueError("La tarea no puede estar vacia.")

        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE tareas
                    SET texto = %s, fecha_limite = %s
                    WHERE id = %s
                    RETURNING id, texto, completada, fecha_limite
                """,
                    (texto_limpio, fecha_limite, tarea_id),
                )
                resultado = cur.fetchone()
            if not resultado:
                conn.rollback()
                raise LookupError("La tarea no existe.")
            conn.commit()
            return dict(resultado)
        finally:
            conn.close()

    def cambiar_estado_tarea(self, tarea_id, completada):
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE tareas
                    SET completada = %s
                    WHERE id = %s
                    RETURNING id, texto, completada, fecha_limite
                """,
                    (bool(completada), tarea_id),
                )
                resultado = cur.fetchone()
            if not resultado:
                conn.rollback()
                raise LookupError("La tarea no existe.")
            conn.commit()
            return dict(resultado)
        finally:
            conn.close()

    def eliminar_tarea(self, tarea_id):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tareas WHERE id = %s RETURNING id", (tarea_id,)
                )
                if not cur.fetchone():
                    conn.rollback()
                    raise LookupError("La tarea no existe.")
            conn.commit()
        finally:
            conn.close()

    def mostrar_tareas(self):
        for tarea in self.obtener_tareas():
            estado = "x" if tarea["completada"] else " "
            fecha = tarea["fecha_limite"]
            fecha_str = f" | Limite: {fecha}" if fecha else ""
            print(f"[{estado}] {tarea['id']}: {tarea['texto']}{fecha_str}")


if __name__ == "__main__":
    gestor = GestorTareas()
    print("\nTareas actuales:")
    gestor.mostrar_tareas()
