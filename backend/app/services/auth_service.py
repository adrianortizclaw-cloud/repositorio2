from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
import random

from sqlalchemy.orm import Session

from ..core.security import hash_token, verify_password
from ..models.user import User, RefreshToken
from ..models.auth_code import AuthCode
from ..core.config import settings


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_refresh_token_record(db: Session, jti: str, token_hash: str, user_id: str, expires_at: datetime) -> RefreshToken:
    token = RefreshToken(jti=jti, token_hash=token_hash, user_id=user_id, expires_at=expires_at)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_refresh_token_by_jti(db: Session, jti: str) -> Optional[RefreshToken]:
    return db.query(RefreshToken).filter(RefreshToken.jti == jti).first()


def revoke_refresh_token(db: Session, token: RefreshToken) -> None:
    token.revoked = True
    token.revoked_at = datetime.utcnow()
    db.add(token)
    db.commit()


def create_auth_code(db: Session, user_id: str, purpose: str = "login") -> str:
    code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=settings.auth_code_expire_minutes)
    record = AuthCode(
        user_id=user_id,
        code_hash=hash_token(code),
        purpose=purpose,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return code


def get_valid_auth_code(db: Session, user_id: str, code: str, purpose: str = "login") -> Optional[AuthCode]:
    record = (
        db.query(AuthCode)
        .filter(AuthCode.user_id == user_id)
        .filter(AuthCode.purpose == purpose)
        .filter(AuthCode.used == False)
        .order_by(AuthCode.created_at.desc())
        .first()
    )
    if not record or record.expires_at < datetime.utcnow():
        return None
    if not verify_password(code, record.code_hash):
        return None
    return record


def mark_auth_code_used(db: Session, record: AuthCode) -> None:
    record.used = True
    db.add(record)
    db.commit()


def send_confirmation_email(user: User, code: str) -> None:
    recipient = user.username
    print(f"[auth] Enviando código {code} a {recipient}")
