from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..models.user import User, RefreshToken


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
