# Agencia Contable Web App

Aplicación web para agencia contable en México con FastAPI, Jinja, SQLite (desarrollo) y PostgreSQL (producción). Incluye sitio público, panel administrativo y carga de imágenes a Firebase Storage.

## Requisitos
- Python 3.12+
- Firebase Service Account JSON (para imágenes)

## Configuración rápida
1. Copia `.env.example` a `.env` y completa las variables necesarias.
2. Instala dependencias:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Ejecuta el servidor:

```bash
uvicorn app.main:app --reload
```

## Credenciales iniciales
- Usuario: `SUPER_ADMIN_USERNAME`
- Password: `SUPER_ADMIN_PASSWORD`

Estos valores se definen en `.env` y se cargan en el primer arranque.

## Firebase Storage
Para almacenar imágenes y videos en Firebase:
- `FIREBASE_CREDENTIALS`: ruta al JSON de Service Account.
- `FIREBASE_BUCKET`: nombre del bucket (ej. `project-id.appspot.com`).

Si Firebase no está configurado, los archivos se guardan localmente en `app/static/uploads`.

## Contacto por correo
Completa la configuración SMTP en `.env` para enviar correos desde el formulario de contacto.

## Rutas principales
- `/` Inicio
- `/about` Nosotros
- `/learn-more` Aprende más
- `/admin/login` Acceso al dashboard

## Deploy (Heroku)
- Configura `DATABASE_URL` como PostgreSQL en el dashboard de Heroku.
- Define variables de entorno (SMTP, Firebase, credenciales admin).
- Usa `Procfile` incluido.
