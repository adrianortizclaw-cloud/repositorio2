from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from ..models.base import Base

    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    from ..models.base import Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
