import psycopg2
from psycopg2.extras import RealDictCursor
import os


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("La variable DATABASE_URL no esta configurada.")
    return psycopg2.connect(database_url, sslmode="require")


def init_db():
    """Inicializa las tablas de usuarios y tareas."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    usuario VARCHAR(50) UNIQUE NOT NULL,
                    contraseña VARCHAR(255) NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS tareas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    texto VARCHAR(500) NOT NULL,
                    completada BOOLEAN DEFAULT FALSE,
                    fecha_limite TIMESTAMP NULL
                )
            """)
        conn.commit()
    finally:
        conn.close()
