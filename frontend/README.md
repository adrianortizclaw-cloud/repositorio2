# Frontend

Interfaz SPA pensada para múltiples equipos y dashboards de análisis dentro de `instagramproyect`.

## Qué incluye
- Dockerfile basado en `node:20-alpine` para mantener la imagen ligera.
- `package.json` + `package-lock.json` (implementación pendiente).
- Variables de entorno definidas en `.env.example`.

## Estructura propuesta
- `src/components/` – componenetes reutilizables (cards, modales, widgets). 
- `src/pages/` – vistas dedicadas a monitores, análisis y pilots de automatización.
- `src/utils/` – utilidades para formateo, llamadas a APIs y almacenamiento temporal.
- `src/hooks/` – lógica compartida (autenticación, polling de tareas).
- `src/assets/` – iconografía, logos y variables estáticas.
- `public/` – entry HTML, favicons y metadatos.

## Comandos útiles
docker build -t instagramproyect-frontend ./frontend

docker run --rm -p 3000:3000 --env-file frontend/.env.example instagramproyect-frontend
