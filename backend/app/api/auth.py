from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..core.config import settings
from ..core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from ..models.user import users_db, UserInDB, TokenPayload
from ..api.dependencies import get_current_user, get_current_active_user, Role, get_token_data

router = APIRouter()


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user_record = users_db.get(form.username)
    if not user_record or not verify_password(form.password, user_record.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    access_token_delta = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_delta = timedelta(days=settings.refresh_token_expire_days)

    access_token = create_access_token(data={"sub": user_record.username, "role": user_record.role}, expires_delta=access_token_delta)
    refresh_token = create_refresh_token(data={"sub": user_record.username}, expires_delta=refresh_token_delta)

    response = Response()
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/"
    )
    response.headers["Authorization"] = f"Bearer {access_token}"
    return {"access_token": access_token, "token_type": "bearer", "role": user_record.role}


@router.post("/refresh")
def refresh(token: TokenPayload = Depends(get_token_data)):
    if token.role == Role.GUEST:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
    access_token_delta = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": token.username, "role": token.role}, expires_delta=access_token_delta)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(settings.refresh_cookie_name, path="/")
    return {"detail": "Sesión cerrada"}


@router.get("/me")
def profile(user: UserInDB = Depends(get_current_active_user)):
    return {"username": user.username, "role": user.role}


@router.get("/admin")
def admin_only(user: UserInDB = Depends(get_current_user(role=Role.ADMIN))):
    return {"msg": f"Bienvenido administrador {user.username}"}
