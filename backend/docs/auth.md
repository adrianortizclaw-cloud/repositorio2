# Autenticación en InstagramProyect

## Roles
- `admin`: acceso a dashboards de monitorización, paneles de control de campañas y auditoría.
- `client`: solo accede a sus propios flujos, métricas y automatizaciones.
- `guest`: estado implícito para rutas públicas (login, marketing, salud).

## Tokens
1. Acceso con `POST /auth/login` (OAuth2 password flow) para recibir `access_token` + cookie `refresh_token`.
2. El `access_token` (JWT) contiene el `role` y un TTL corto para limitar ventanas de exposición.
3. El `refresh_token` se guarda en cookie `HttpOnly` y se rota cada refresh.
4. `Authorization: Bearer <access>` acompaña las llamadas API.

## Control de acceso
- Middleware `get_current_user(role=...)` permite proteger rutas sensibles.
- `Role.ADMIN` y `Role.CLIENT` se usan para diferenciar permisos.
- Si no hay token válido se trata al usuario como `guest`.

## Pasos siguientes
- Conectar `users_db` con SQLAlchemy + tabla real de `users`.
- Registrar cada refresh token en la tabla `refresh_tokens` y permitir revocaciones.
- Añadir auditoría de sesiones (IP, user agent) y alertas de comportamiento sospechoso.
