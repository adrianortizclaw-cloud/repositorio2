from ..core.time import utcnow
from sqlalchemy import Column, String, Boolean, DateTime

from .base import Base


class InstagramAuthState(Base):
    __tablename__ = "instagram_auth_states"

    id = Column(String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    state = Column(String(128), unique=True, index=True)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)


class InstagramSession(Base):
    __tablename__ = "instagram_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    session_id = Column(String(128), unique=True, index=True)
    ig_user_id = Column(String(120), index=True)
    username = Column(String(120), nullable=True)
    name = Column(String(120), nullable=True)
    access_token_encrypted = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)
