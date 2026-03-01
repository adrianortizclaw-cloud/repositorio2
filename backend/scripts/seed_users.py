"""Seed script para usuarios iniciales."""
from app.core.security import get_password_hash
from app.database.session import SessionLocal, init_db
from app.models.user import User


DEFAULT_USERS = [
    {"username": "client@example.com", "password": "secret", "full_name": "Cliente Instagram", "role": "client"},
    {"username": "admin@example.com", "password": "secret", "full_name": "Admin Instagram", "role": "admin"},
]


def seed_users() -> None:
    init_db()
    db = SessionLocal()
    try:
        for entry in DEFAULT_USERS:
            user = db.query(User).filter(User.username == entry["username"]).first()
            if user:
                continue
            db.add(
                User(
                    username=entry["username"],
                    full_name=entry["full_name"],
                    role=entry["role"],
                    hashed_password=get_password_hash(entry["password"]),
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
