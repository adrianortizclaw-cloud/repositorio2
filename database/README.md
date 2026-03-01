# Database

Instancia Postgres para almacenar datos de automatización, deduplicación y analítica.

## Configuración
- Dockerfile basado en `postgres:16-alpine` para mantener la imagen ligera.
- El volumen `/var/lib/postgresql/data` queda montado desde `docker-compose`.
- Las variables del contenedor se parametrizan desde `database/.env.example`.

## Estrategia de backups (plan)
1. Copias diarias en frío usando `pg_dump` desde otro contenedor sincronizado con los volúmenes.
2. Transferencia incremental a un bucket S3 (o compatible) con `rclone`/`aws-cli` en un job separado.
3. Retención: conservar los últimos 7 snapshots y rotar con `DELETE` basado en fecha.
4. Restauración rápida documentada en `database/restore.sh` (implementación futura).

## Próximos pasos
- Añadir scripts de `init` para crear esquemas y usuarios.
- Definir triggers para auditoría y replicación hacia read replicas.
