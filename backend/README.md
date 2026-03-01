# Backend

Servicio API para cron jobs, ingestión de métricas y automatización dentro de `instagramproyect`.

## Puntos clave
- `Dockerfile` minimalista con Python 3.12 y Uvicorn.
- `requirements.txt` como entrada para definir dependencias externas.
- Variables de entorno en `.env.example` para separar configuración.

## Despliegue local
docker build -t instagramproyect-backend ./backend
docker run --rm -p 8000:8000 --env-file backend/.env.example instagramproyect-backend
