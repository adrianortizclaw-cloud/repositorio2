# Esquema de autenticación

## Tablas sugeridas
1. `users`
   - `id` (UUID)
   - `email` (unique)
   - `full_name`
   - `role` (`admin`/`client`)
   - `hashed_password`
   - `is_active`
   - `created_at`, `updated_at`

2. `refresh_tokens`
   - `id` (UUID)
   - `user_id` (FK a `users`)
   - `token` (hash del refresh token)
   - `created_at`, `expires_at`
   - `revoked` (bool)
   - `user_agent`, `ip`

## Flujo
- `POST /auth/login`: valida contraseña y crea tokens (access + refresh).
- El refresh token se guarda en la tabla para poder revocarlo desde logout o auditoría.
- `POST /auth/refresh`: consulta `refresh_tokens`, comprueba expiración/revocado, renueva access token, rota el refresh (opera en transacción).
- `POST /auth/logout`: marca `revoked=true` y borra cookie.

## Claves de seguridad
- El `refresh_token` no se almacena en texto plano; guarda su hash (descifra la cookie para comparar con `bcrypt` o similar).
- Usa `role` y `scopes` en el `access token` para distinguir rutas protegidas.
- Mantén una política de re-autenticación cada 14 días y posibilidad de invalidar sessions en cascada.
