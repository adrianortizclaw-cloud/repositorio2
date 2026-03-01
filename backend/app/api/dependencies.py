from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.roles import Role
from ..core.security import decode_token
from ..database.session import SessionLocal
from ..models.user import User
from ..schemas.token import TokenPayload

security_scheme = HTTPBearer(auto_error=False)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token_data(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> TokenPayload:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no proporcionado")
    return decode_token(credentials.credentials)


def get_current_user(role: Optional[Role] = None):
    def inner(token: TokenPayload = Depends(get_token_data), db: Session = Depends(get_db)) -> User:
        user = db.query(User).filter(User.username == token.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
        if role and token.role != role.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos")
        return user
    return inner


def get_current_active_user(token: TokenPayload = Depends(get_token_data), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == token.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return user
