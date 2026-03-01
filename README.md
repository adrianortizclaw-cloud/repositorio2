# InstagramProyect

Este repositorio (`instagramproyect`) contiene la infraestructura base del proyecto profesional: frontend, backend y base de datos separados, cada uno con su Dockerfile, y todo orquestado via Docker Compose.

## Arquitectura
1. **Frontend** — SPA ligera (Node) que ofrece dashboards multiusuario.
2. **Backend** — API en FastAPI para orquestar tareas, flujos de monitoreo y procesos de automatización.
3. **Database** — Postgres dedicado con estrategia de backups documentada.
4. **CI/CD** — Flujo en GitHub Actions que valida builds y prepara imágenes.

## Flujo de despliegue
```bash
# desde la raíz
cp .env.example .env
docker compose up --build
```

Las aplicaciones se comunican mediante la red interna de Docker Compose, por lo que el deploy puede escalar fácilmente (remoto, k8s, etc.).
