import uuid
from ..core.time import utcnow
from sqlalchemy import Column, String, DateTime

from ..models.base import Base


class PendingRegistration(Base):
    __tablename__ = "pending_registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="client")
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
