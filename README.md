# Gestor de Tareas

Aplicacion web para gestionar tareas con fechas limite. Backend en Python y frontend estatico en HTML, CSS y JavaScript.

## Funcionalidades

- Agregar tareas con texto y fecha limite
- Mostrar todas las tareas
- Editar tareas existentes
- Marcar tareas como completadas o pendientes
- Eliminar tareas
- Indicador visual de tareas vencidas

## Requisitos

- Python 3.8+
- PostgreSQL (NeonDB o cualquier PostgreSQL con SSL)

## Instalacion

1. Clonar el repositorio
2. Crear un archivo `.env` en la raiz del proyecto:

```
DATABASE_URL=postgresql://usuario:password@host/dbname?sslmode=require
```

3. Instalar dependencias:

```powershell
cd backend
pip install -r requirements.txt
```

## Como ejecutar

### Backend (terminal 1)

```powershell
cd backend
python api_server.py
```

El servidor estara disponible en `http://localhost:8000`

### Frontend (terminal 2)

Abrir `frontend/index.html` con un servidor local como Live Server en VS Code.

## API REST

### Listar tareas

```http
GET /api/tareas
```

### Crear tarea

```http
POST /api/tareas
Content-Type: application/json

{
  "texto": " Nueva tarea",
  "fecha_limite": "2026-04-20T15:30:00"
}
```

### Editar tarea

```http
PUT /api/tareas
Content-Type: application/json

{
  "id": 1,
  "texto": "Tarea actualizada",
  "fecha_limite": "2026-04-25T10:00:00"
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

```
backend/
  api_server.py       - Servidor HTTP con API REST
  gestor_tareas.py    - Logica de acceso a datos
  requirements.txt   - Dependencias Python
frontend/
  index.html          - Pagina principal
  styles.css          - Estilos CSS
  script.js           - Logica de cliente
.env                   - Variables de entorno (no incluir en git)
.env.example           - Plantilla de variables de entorno
```
