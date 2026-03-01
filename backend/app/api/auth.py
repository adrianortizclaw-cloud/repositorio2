from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.roles import Role
from ..core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_token,
    decode_token,
)
from ..database.session import get_db
from ..models.user import User
from ..schemas.token import TokenPayload
from ..services.auth_service import (
    get_user_by_username,
    create_refresh_token_record,
    get_refresh_token_by_jti,
    revoke_refresh_token,
)
from ..api.dependencies import get_current_user, get_current_active_user

router = APIRouter()


def _build_refresh_response(access_token: str, refresh_token: str, role: str) -> JSONResponse:
    response = JSONResponse({"access_token": access_token, "token_type": "bearer", "role": role})
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )
    return response


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_record = get_user_by_username(db, form.username)
    if not user_record or not verify_password(form.password, user_record.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    access_token_delta = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_delta = timedelta(days=settings.refresh_token_expire_days)

    refresh_jti = uuid4().hex
    refresh_token = create_refresh_token(
        data={"sub": user_record.username, "role": user_record.role, "jti": refresh_jti},
        expires_delta=refresh_token_delta,
    )
    refresh_hash = hash_token(refresh_token)
    create_refresh_token_record(db, refresh_jti, refresh_hash, user_record.id, datetime.utcnow() + refresh_token_delta)

    access_token = create_access_token(data={"sub": user_record.username, "role": user_record.role}, expires_delta=access_token_delta)
    return _build_refresh_response(access_token, refresh_token, user_record.role)


@router.post("/refresh")
def refresh(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de refresco no proporcionado")

    token_payload = decode_token(refresh_token)
    if token_payload.token_type != "refresh" or not token_payload.jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    token_record = get_refresh_token_by_jti(db, token_payload.jti)
    if not token_record or token_record.revoked or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado o revocado")

    user_record: User = get_user_by_username(db, token_payload.username)
    if not user_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    revoke_refresh_token(db, token_record)

    access_token_delta = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_delta = timedelta(days=settings.refresh_token_expire_days)

    new_refresh_jti = uuid4().hex
    new_refresh_token = create_refresh_token(
        data={"sub": user_record.username, "role": user_record.role, "jti": new_refresh_jti},
        expires_delta=refresh_token_delta,
    )
    new_refresh_hash = hash_token(new_refresh_token)
    create_refresh_token_record(db, new_refresh_jti, new_refresh_hash, user_record.id, datetime.utcnow() + refresh_token_delta)

    new_access_token = create_access_token(data={"sub": user_record.username, "role": user_record.role}, expires_delta=access_token_delta)
    return _build_refresh_response(new_access_token, new_refresh_token, user_record.role)


@router.post("/logout")
def logout(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if refresh_token:
        try:
            token_payload = decode_token(refresh_token)
        except HTTPException:
            token_payload = None
        if token_payload and token_payload.jti:
            token_record = get_refresh_token_by_jti(db, token_payload.jti)
            if token_record:
                revoke_refresh_token(db, token_record)
    response = JSONResponse({"detail": "Sesión cerrada"})
    response.delete_cookie(settings.refresh_cookie_name, path="/")
    return response


@router.get("/me")
def profile(user: User = Depends(get_current_active_user)):
    return {"username": user.username, "role": user.role}


@router.get("/admin")
def admin_only(user: User = Depends(get_current_user(role=Role.ADMIN))):
    return {"msg": f"Bienvenido administrador {user.username}"}
