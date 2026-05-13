# Sistema de Reservas de Espacios

Proyecto grupal (Django + PostgreSQL) para gestionar espacios físicos, horarios y reservas con roles de administrador y usuario.

## Requisitos

- Python 3.12+ (recomendado 3.12.x)
- `pip` actualizado

### Dependencias principales

| Paquete | Uso |
|--------|-----|
| Django | Framework web |
| psycopg2-binary | Adaptador PostgreSQL |
| Pillow | Imágenes de perfil |
| django-widget-tweaks | Widgets en formularios |
| dj-database-url | `DATABASE_URL` en producción |
| whitenoise | Estáticos en producción |
| gunicorn | Servidor WSGI (Render/Railway) |
| reportlab | Exportación PDF (módulo reporting) |
| openpyxl | Exportación Excel (módulo reporting) |

Instalación:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Configuración local (SQLite)

Por defecto el proyecto usa SQLite. Crea las tablas y un superusuario:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Poblado opcional de espacios (si existe el comando):

```bash
python manage.py seed_espacios
```

## Ejecución en desarrollo

```bash
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` (redirige al login). El **dashboard analítico** (solo administradores) está en `http://127.0.0.1:8000/reporting/`.

### Estáticos

Antes de desplegar o para comprobar la recolección de estáticos:

```bash
python manage.py collectstatic --noinput
```

## PostgreSQL

### Opción A — `DATABASE_URL` (Render, Railway, Docker)

Define la variable de entorno `DATABASE_URL` (formato estándar, por ejemplo `postgres://user:pass@host:5432/dbname`). El archivo `reservas_espacios/settings.py` configura la base con `dj-database-url`.

### Opción B — variables sueltas

```text
DB_NAME=reservas_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

Sin `DATABASE_URL` ni `DB_NAME`, el proyecto sigue usando SQLite.

## Módulo Reporting (Integrante 4)

Ruta base: `/reporting/`

- Indicadores y KPIs con datos reales de `reservas`, `espacios` y `accounts`.
- Gráficos: **Chart.js** (ocupación semanal y reservas por mes) y **Plotly** (reservas por sala).
- Exportación **PDF** y **Excel** con filtro por fechas.
- **FullCalendar**: calendario interactivo alimentado por API interna.

Solo usuarios con rol **administrador** pueden acceder.

## Despliegue

### Variables de entorno recomendadas (producción)

| Variable | Descripción |
|----------|-------------|
| `DEBUG` | `False` |
| `SECRET_KEY` o `DJANGO_SECRET_KEY` | Clave segura aleatoria |
| `ALLOWED_HOSTS` | `tudominio.onrender.com` o lista separada por comas |
| `CSRF_TRUSTED_ORIGINS` | `https://tudominio.onrender.com` |
| `DATABASE_URL` | Cadena PostgreSQL del proveedor |

### Render.com

1. Crea un **PostgreSQL** y un **Web Service** apuntando al repositorio.
2. En el build del servicio web suele usarse:

   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

3. Comando de arranque (también en `Procfile`):

   ```bash
   gunicorn reservas_espacios.wsgi:application --bind 0.0.0.0:$PORT
   ```

4. Opcional: importa el blueprint `render.yaml` desde el panel de Render y ajusta nombres.

### Railway.app

1. Nuevo proyecto desde GitHub; añade plugin **PostgreSQL**.
2. Railway inyecta `DATABASE_URL` automáticamente.
3. Define `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` con la URL pública HTTPS que te asigne Railway.
4. Mismo comando de build y `gunicorn` que en Render.

### Archivos incluidos

- `Procfile` — comando web para plataformas tipo Heroku/Render.
- `render.yaml` — ejemplo de blueprint con Postgres + web.

## Flujo de ramas (equipo)

- `main`: estable; no desarrollar directamente sobre ella.
- `dev`: integración.
- Trabajo en ramas `feature-*`; merge hacia `dev` (por ejemplo `feature-4` para reporting).

## Licencia / uso académico

Proyecto final de electiva — uso educativo.
