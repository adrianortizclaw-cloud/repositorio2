import random
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.roles import Role
from ..core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_token,
    decode_token,
    get_password_hash,
)
from ..database.session import get_db
from ..models.user import User
from ..models.pending_registration import PendingRegistration
from ..services.auth_service import (
    get_user_by_username,
    create_refresh_token_record,
    get_refresh_token_by_jti,
    revoke_refresh_token,
    create_pending_registration,
    get_pending_registration,
    delete_pending_registration,
    create_auth_code,
    get_valid_auth_code,
    mark_auth_code_used,
    send_confirmation_email,
)
from ..api.dependencies import get_current_user, get_current_active_user

router = APIRouter()


class RegisterPayload(BaseModel):
    username: EmailStr
    password: str
    role: Role = Role.CLIENT
    full_name: Optional[str] = None


class ConfirmPayload(BaseModel):
    username: EmailStr
    code: str
    purpose: Optional[str] = "register"


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


def _issue_tokens(db: Session, user_record: User) -> JSONResponse:
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


def _send_confirmation_code(db: Session, pending: PendingRegistration) -> JSONResponse:
    code = f"{random.randint(0, 999999):06d}"
    expires = datetime.utcnow() + timedelta(minutes=settings.auth_code_expire_minutes)
    create_auth_code(db, code, expires, purpose="register", pending=pending)
    send_confirmation_email(pending.username, code)
    return JSONResponse({
        "detail": "Código enviado",
        "code_preview": code,
        "username": pending.username,
        "purpose": "register",
    })


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> JSONResponse:
    user_record = get_user_by_username(db, form.username)
    if not user_record or not verify_password(form.password, user_record.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    return _issue_tokens(db, user_record)


@router.post("/register")
def register(payload: RegisterPayload, db: Session = Depends(get_db)) -> JSONResponse:
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ya registrado")
    if get_pending_registration(db, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya se ha solicitado una confirmación para ese email")
    expires = datetime.utcnow() + timedelta(minutes=settings.auth_code_expire_minutes)
    pending = create_pending_registration(db, payload.username, get_password_hash(payload.password), payload.role.value, payload.full_name, expires)
    return _send_confirmation_code(db, pending)


@router.post("/confirm")
def confirm(payload: ConfirmPayload, db: Session = Depends(get_db)) -> JSONResponse:
    if payload.purpose == "register":
        pending = get_pending_registration(db, payload.username)
        if not pending:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
        code_record = get_valid_auth_code(db, pending.username, payload.code, purpose="register")
        if not code_record:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido o expirado")
        mark_auth_code_used(db, code_record)
        user = User(
            username=pending.username,
            full_name=pending.full_name,
            role=pending.role,
            hashed_password=pending.hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        delete_pending_registration(db, pending)
        return _issue_tokens(db, user)
    user_record = get_user_by_username(db, payload.username)
    if not user_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    code_record = get_valid_auth_code(db, user_record.username, payload.code, purpose=payload.purpose or "login")
    if not code_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido o expirado")
    mark_auth_code_used(db, code_record)
    return _issue_tokens(db, user_record)


@router.post("/refresh")
def refresh(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)) -> JSONResponse:
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

    return _issue_tokens(db, user_record)


@router.post("/logout")
def logout(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)) -> JSONResponse:
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
def profile(user: User = Depends(get_current_active_user)) -> JSONResponse:
    return JSONResponse({"username": user.username, "role": user.role})


@router.get("/admin")
def admin_only(user: User = Depends(get_current_user(role=Role.ADMIN))) -> JSONResponse:
    return JSONResponse({"msg": f"Bienvenido administrador {user.username}"})
