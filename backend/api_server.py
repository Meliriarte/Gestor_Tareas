import os

from app import app


if __name__ == "__main__":
    # Mantiene compatibilidad con ejecuciones antiguas de este archivo.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
