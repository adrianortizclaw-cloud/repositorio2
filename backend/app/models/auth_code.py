import uuid
from ..core.time import utcnow
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..models.base import Base


class AuthCode(Base):
    __tablename__ = "auth_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    pending_registration_id = Column(String(36), ForeignKey("pending_registrations.id"), nullable=True)
    code_hash = Column(String(255), nullable=False)
    purpose = Column(String(32), nullable=False, default="register")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="auth_codes")
