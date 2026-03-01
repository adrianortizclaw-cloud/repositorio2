# Backend

Servicio API para cron jobs, ingestión de métricas y automatización dentro de `instagramproyect`.

## Puntos clave
- `Dockerfile` minimalista con Python 3.12 y Uvicorn.
- `requirements.txt` como entrada para definir dependencias externas.
- Variables de entorno en `.env.example` para separar configuración.

## Estructura propuesta
- `app/api/` – routers y endpoints que exponen el API REST/GraphQL.
- `app/core/` – configuración de la app, middlewares, clientes HTTP y variables globales.
- `app/models/` – modelos Pydantic + esquemas de base de datos.
- `app/services/` – lógica de negocio (procesos de Instagram, programación de jobs, deduplicación).
- `app/workers/` – tareas asíncronas (Celery/RQ) y sincronización de hilos de trabajo.
- `scripts/` – utilidades CLI para mantenimiento (migraciones, importaciones, dumps).
- `tests/` – pruebas unitarias y de integración.

## Despliegue local
docker build -t instagramproyect-backend ./backend
docker run --rm -p 8000:8000 --env-file backend/.env.example instagramproyect-backend
