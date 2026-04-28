# Gestor de Tareas

Aplicacion web para gestionar tareas con autenticacion de usuarios, fechas limite y seguimiento visual del progreso.

Demo:
https://gestor-tareas-mdht.onrender.com/

## Funcionalidades

- Registro e inicio de sesion
- Crear tareas con fecha y hora limite opcional
- Editar texto y fecha limite de una tarea
- Marcar tareas como completadas o pendientes
- Eliminar tareas
- Buscar tareas por texto
- Filtrar por todas, pendientes, completadas o vencidas
- Resumen visual con contadores y porcentaje de avance
- Indicador visual de tareas vencidas

## Tecnologias

- Frontend: HTML, CSS y JavaScript
- Backend: Flask
- Base de datos: PostgreSQL

## Requisitos

- Python 3.8+
- PostgreSQL accesible mediante `DATABASE_URL`

## Variables de entorno

Crea un archivo `.env` en la raiz del proyecto con al menos:

```env
DATABASE_URL=postgresql://usuario:password@host/dbname?sslmode=require
SECRET_KEY=una-clave-segura
PORT=5000
```

Notas:

- `SECRET_KEY` se usa para la sesion de Flask.
- `PORT` es opcional en local; por defecto se usa `5000`.

## Instalacion

```powershell
cd backend
pip install -r requirements.txt
```

## Ejecucion local

Desde la carpeta `backend`:

```powershell
python app.py
```

La aplicacion quedara disponible en:

`http://localhost:5000`

No hace falta levantar un servidor aparte para el frontend: Flask sirve `index.html`, `styles.css` y `script.js` desde la raiz del proyecto.

## API REST

La API usa sesion de Flask. Para operar con tareas primero debes autenticarte.

## Autenticacion

### Registrar usuario

```http
POST /api/registro
Content-Type: application/json

{
  "nombre": "Maria",
  "usuario": "maria",
  "contrasena": "secreta"
}
```

### Iniciar sesion

```http
POST /api/login
Content-Type: application/json

{
  "usuario": "maria",
  "contrasena": "secreta"
}
```

### Cerrar sesion

```http
POST /api/logout
```

### Verificar sesion

```http
GET /api/sesion
```

## Tareas

### Listar tareas

```http
GET /api/tareas
```

Respuesta esperada:

```json
{
  "tareas": [
    {
      "id": 1,
      "texto": "Preparar presentacion",
      "completada": false,
      "fecha_limite": "2026-04-28T23:59:00"
    }
  ]
}
```

### Crear tarea

```http
POST /api/tareas
Content-Type: application/json

{
  "texto": "Nueva tarea",
  "fecha_limite": "2026-04-28T23:59:00"
}
```

### Editar tarea

```http
PUT /api/tareas
Content-Type: application/json

{
  "id": 1,
  "texto": "Tarea actualizada",
  "fecha_limite": "2026-04-29T10:00:00"
}
```

Para quitar la fecha limite, envia:

```json
{
  "id": 1,
  "texto": "Tarea sin fecha",
  "fecha_limite": null
}
```

### Cambiar estado

```http
PATCH /api/tareas
Content-Type: application/json

{
  "id": 1,
  "completada": true
}
```

### Eliminar tarea

```http
DELETE /api/tareas
Content-Type: application/json

{
  "id": 1
}
```

## Estructura del proyecto

```text
backend/
  app.py             - Backend principal en Flask
  db.py              - Conexion e inicializacion de la base de datos
  models.py          - Acceso a datos de usuarios y tareas
  api_server.py      - Servidor alterno simple para tareas
  gestor_tareas.py   - Logica usada por el servidor alterno
  requirements.txt   - Dependencias Python
index.html           - Interfaz principal
styles.css           - Estilos de la aplicacion
script.js            - Logica del frontend
.env.example         - Plantilla de variables de entorno
```
