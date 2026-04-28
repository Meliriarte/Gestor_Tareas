from datetime import datetime

from flask import Flask, request, jsonify, session, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from db import init_db
from models import Usuario, Tarea

app = Flask(__name__, template_folder=BASE_DIR)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("SECRET_KEY", "gestor-tareas-key-desarrollo")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False

init_db()


def serializar_tarea(tarea):
    tarea_serializada = dict(tarea)
    fecha_limite = tarea_serializada.get("fecha_limite")

    if isinstance(fecha_limite, datetime):
        tarea_serializada["fecha_limite"] = fecha_limite.strftime("%Y-%m-%dT%H:%M:%S")

    return tarea_serializada


def serializar_tareas(tareas):
    return [serializar_tarea(tarea) for tarea in tareas]


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route("/api/registro", methods=["POST"])
def registro():
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    usuario = data.get("usuario", "").strip()
    contraseña = data.get("contraseña", "")

    if not nombre or not usuario or not contraseña:
        return jsonify({"error": "Todos los campos son requeridos."}), 400

    try:
        contraseña_hash = generate_password_hash(contraseña)
        nuevo_usuario = Usuario.crear(nombre, usuario, contraseña_hash)
        session["usuario_id"] = nuevo_usuario["id"]
        session["nombre"] = nuevo_usuario["nombre"]
        return jsonify(
            {
                "mensaje": "Cuenta creada correctamente.",
                "nombre": nuevo_usuario["nombre"],
            }
        ), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error al crear la cuenta."}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data.get("usuario", "").strip()
    contraseña = data.get("contraseña", "")

    if not usuario or not contraseña:
        return jsonify({"error": "Usuario y contraseña son requeridos."}), 400

    usuario_db = Usuario.buscar_por_usuario(usuario)
    if not usuario_db or not check_password_hash(usuario_db.get("contraseña"), contraseña):
        return jsonify({"error": "Usuario o contraseña incorrectos."}), 401

    session["usuario_id"] = usuario_db["id"]
    session["nombre"] = usuario_db["nombre"]
    return jsonify({"mensaje": "Login exitoso.", "nombre": usuario_db["nombre"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada."})


@app.route("/api/sesion", methods=["GET"])
def verificar_sesion():
    if "usuario_id" in session:
        return jsonify({"autenticado": True, "nombre": session.get("nombre")})
    return jsonify({"autenticado": False})


@app.route("/api/tareas", methods=["GET"])
def obtener_tareas():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado."}), 401

    tareas = Tarea.obtener_tareas(session["usuario_id"])
    return jsonify({"tareas": serializar_tareas(tareas)})


@app.route("/api/tareas", methods=["POST"])
def agregar_tarea():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado."}), 401

    data = request.get_json()
    texto = data.get("texto", "")
    fecha_limite = data.get("fecha_limite") or None

    try:
        tarea = Tarea.agregar(session["usuario_id"], texto, fecha_limite)
        return jsonify({"mensaje": "Tarea agregada.", "tarea": serializar_tarea(tarea)}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tareas", methods=["PUT"])
def editar_tarea():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado."}), 401

    data = request.get_json()
    tarea_id = data.get("id")
    texto = data.get("texto", "")
    fecha_limite = data.get("fecha_limite") or None

    if not tarea_id:
        return jsonify({"error": "ID requerido."}), 400

    try:
        tarea = Tarea.editar(tarea_id, session["usuario_id"], texto, fecha_limite)
        return jsonify({"mensaje": "Tarea editada.", "tarea": serializar_tarea(tarea)})
    except (ValueError, LookupError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tareas", methods=["PATCH"])
def cambiar_estado():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado."}), 401

    data = request.get_json()
    tarea_id = data.get("id")
    completada = data.get("completada", False)

    if not tarea_id:
        return jsonify({"error": "ID requerido."}), 400

    try:
        tarea = Tarea.cambiar_estado(tarea_id, session["usuario_id"], completada)
        return jsonify({"mensaje": "Estado actualizado.", "tarea": serializar_tarea(tarea)})
    except LookupError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tareas", methods=["DELETE"])
def eliminar_tarea():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado."}), 401

    data = request.get_json()
    tarea_id = data.get("id")

    if not tarea_id:
        return jsonify({"error": "ID requerido."}), 400

    try:
        Tarea.eliminar(tarea_id, session["usuario_id"])
        return jsonify({"mensaje": "Tarea eliminada."})
    except LookupError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
