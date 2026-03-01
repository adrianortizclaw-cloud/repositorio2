from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from ..core.security import hash_token, verify_password
from ..models.user import User, RefreshToken
from ..models.auth_code import AuthCode
from ..models.pending_registration import PendingRegistration
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


def create_pending_registration(db: Session, username: str, hashed_password: str, role: str, full_name: Optional[str], expires_at: datetime) -> PendingRegistration:
    pending = PendingRegistration(
        username=username,
        hashed_password=hashed_password,
        role=role,
        full_name=full_name,
        expires_at=expires_at,
    )
    db.add(pending)
    db.commit()
    db.refresh(pending)
    return pending


def get_pending_registration(db: Session, username: str) -> Optional[PendingRegistration]:
    return db.query(PendingRegistration).filter(PendingRegistration.username == username).first()


def delete_pending_registration(db: Session, pending: PendingRegistration) -> None:
    db.delete(pending)
    db.commit()


def create_auth_code(db: Session, code: str, expires_at: datetime, purpose: str = "register", user: Optional[User] = None, pending: Optional[PendingRegistration] = None) -> AuthCode:
    record = AuthCode(
        user_id=user.id if user else None,
        pending_registration_id=pending.id if pending else None,
        code_hash=hash_token(code),
        purpose=purpose,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_valid_auth_code(db: Session, username: str, code: str, purpose: str = "register") -> Optional[AuthCode]:
    query = db.query(AuthCode).filter(AuthCode.purpose == purpose, AuthCode.used == False)
    if purpose == "register":
        pending = get_pending_registration(db, username)
        if not pending:
            return None
        query = query.filter(AuthCode.pending_registration_id == pending.id)
    else:
        user = get_user_by_username(db, username)
        if not user:
            return None
        query = query.filter(AuthCode.user_id == user.id)
    record = query.order_by(AuthCode.created_at.desc()).first()
    if not record or record.expires_at < datetime.utcnow():
        return None
    if not verify_password(code, record.code_hash):
        return None
    return record


def mark_auth_code_used(db: Session, record: AuthCode) -> None:
    record.used = True
    db.add(record)
    db.commit()


def send_confirmation_email(email: str, code: str) -> None:
    print(f"[auth] Enviando código {code} a {email}")
