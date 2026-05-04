import os

import psycopg2


PASSWORD_COLUMN = "contrasena"
LEGACY_PASSWORD_COLUMNS = ("contraseña", "contraseÃ±a")


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("La variable DATABASE_URL no esta configurada.")
    return psycopg2.connect(database_url, sslmode="require")


def _column_exists(cur, table_name, column_name):
    cur.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        (table_name, column_name),
    )
    return cur.fetchone() is not None


def _migrar_columna_contrasena(cur):
    cur.execute(
        f"ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS {PASSWORD_COLUMN} VARCHAR(255)"
    )

    for legacy_column in LEGACY_PASSWORD_COLUMNS:
        if not _column_exists(cur, "usuarios", legacy_column):
            continue

        # Copia el valor heredado para no romper usuarios existentes.
        cur.execute(
            f"""
            UPDATE usuarios
            SET {PASSWORD_COLUMN} = COALESCE({PASSWORD_COLUMN}, "{legacy_column}")
            WHERE {PASSWORD_COLUMN} IS NULL AND "{legacy_column}" IS NOT NULL
            """
        )

    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM usuarios
        WHERE {PASSWORD_COLUMN} IS NULL
        """
    )
    usuarios_sin_contrasena = cur.fetchone()[0]
    if usuarios_sin_contrasena == 0:
        cur.execute(
            f"ALTER TABLE usuarios ALTER COLUMN {PASSWORD_COLUMN} SET NOT NULL"
        )


def init_db():
    """Inicializa las tablas base y migra columnas legadas si existen."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    usuario VARCHAR(50) UNIQUE NOT NULL,
                    {PASSWORD_COLUMN} VARCHAR(255) NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tareas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    texto VARCHAR(500) NOT NULL,
                    completada BOOLEAN DEFAULT FALSE,
                    fecha_limite TIMESTAMP NULL
                )
                """
            )

            _migrar_columna_contrasena(cur)
        conn.commit()
    finally:
        conn.close()
