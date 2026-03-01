from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.security import decode_token, get_token_role
from ..models.user import TokenPayload, UserInDB, users_db

security_scheme = HTTPBearer(auto_error=False)

class Role(str):
    GUEST = "guest"
    CLIENT = "client"
    ADMIN = "admin"


def get_token_data(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> TokenPayload:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no proporcionado")
    return decode_token(credentials.credentials)


def get_current_user(role: Optional[Role] = None):
    def inner(token: TokenPayload = Depends(get_token_data)) -> UserInDB:
        user = users_db.get(token.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
        if role and token.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos")
        return user
    return inner


def get_current_active_user(token: TokenPayload = Depends(get_token_data)) -> UserInDB:
    user = users_db.get(token.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return user
