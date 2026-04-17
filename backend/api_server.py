import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from gestor_tareas import GestorTareas


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("La variable DATABASE_URL no esta configurada.")
gestor = GestorTareas(database_url)


class TareasHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/tareas":
            self._send_json({"tareas": gestor.obtener_tareas()})
            return
        self._send_json({"error": "Ruta no encontrada."}, status=404)

    def do_POST(self):
        route = urlparse(self.path).path
        if route != "/api/tareas":
            self._send_json({"error": "Ruta no encontrada."}, status=404)
            return

        try:
            data = self._read_json_body()
            fecha_limite = data.get("fecha_limite") or None
            nueva_tarea = gestor.agregar_tarea(data.get("texto", ""), fecha_limite)
        except json.JSONDecodeError:
            self._send_json(
                {"error": "El cuerpo de la solicitud no es JSON valido."}, status=400
            )
            return
        except ValueError as error:
            self._send_json({"error": str(error)}, status=400)
            return

        self._send_json(
            {"mensaje": "Tarea agregada correctamente.", "tarea": nueva_tarea},
            status=201,
        )

    def do_PUT(self):
        route = urlparse(self.path).path
        if route != "/api/tareas":
            self._send_json({"error": "Ruta no encontrada."}, status=404)
            return

        try:
            data = self._read_json_body()
            fecha_limite = data.get("fecha_limite") or None
            tarea_actualizada = gestor.editar_tarea(
                int(data.get("id")),
                data.get("texto", ""),
                fecha_limite,
            )
        except TypeError:
            self._send_json({"error": "Debes enviar un id valido."}, status=400)
            return
        except ValueError as error:
            self._send_json({"error": str(error)}, status=400)
            return
        except LookupError as error:
            self._send_json({"error": str(error)}, status=404)
            return
        except json.JSONDecodeError:
            self._send_json(
                {"error": "El cuerpo de la solicitud no es JSON valido."}, status=400
            )
            return

        self._send_json(
            {"mensaje": "Tarea editada correctamente.", "tarea": tarea_actualizada}
        )

    def do_PATCH(self):
        route = urlparse(self.path).path
        if route != "/api/tareas":
            self._send_json({"error": "Ruta no encontrada."}, status=404)
            return

        try:
            data = self._read_json_body()
            tarea_actualizada = gestor.cambiar_estado_tarea(
                int(data.get("id")),
                data.get("completada", False),
            )
        except TypeError:
            self._send_json({"error": "Debes enviar un id valido."}, status=400)
            return
        except LookupError as error:
            self._send_json({"error": str(error)}, status=404)
            return
        except json.JSONDecodeError:
            self._send_json(
                {"error": "El cuerpo de la solicitud no es JSON valido."}, status=400
            )
            return

        mensaje = (
            "Tarea marcada como completada."
            if tarea_actualizada["completada"]
            else "Tarea marcada como pendiente."
        )
        self._send_json({"mensaje": mensaje, "tarea": tarea_actualizada})

    def do_DELETE(self):
        route = urlparse(self.path).path
        if route != "/api/tareas":
            self._send_json({"error": "Ruta no encontrada."}, status=404)
            return

        try:
            data = self._read_json_body()
            gestor.eliminar_tarea(int(data.get("id")))
        except TypeError:
            self._send_json({"error": "Debes enviar un id valido."}, status=400)
            return
        except LookupError as error:
            self._send_json({"error": str(error)}, status=404)
            return
        except json.JSONDecodeError:
            self._send_json(
                {"error": "El cuerpo de la solicitud no es JSON valido."}, status=400
            )
            return

        self._send_json({"mensaje": "Tarea eliminada correctamente."})

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=TareasHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor disponible en http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
