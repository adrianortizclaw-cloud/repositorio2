from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..schemas.token import TokenPayload
from .config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def hash_token(value: str) -> str:
    return pwd_context.hash(value)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    username: Optional[str] = payload.get("sub")
    role: str = payload.get("role", "guest")
    token_type: str = payload.get("type", "access")
    jti: Optional[str] = payload.get("jti")
    if username is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return TokenPayload(username=username, role=role, token_type=token_type, jti=jti)


def get_token_role_value(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return payload.get("role", "guest")


def encrypt_secret(value: str) -> str:
    from cryptography.fernet import Fernet

    digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    f = Fernet(key)
    return f.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    from cryptography.fernet import Fernet

    digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    f = Fernet(key)
    return f.decrypt(value.encode("utf-8")).decode("utf-8")
