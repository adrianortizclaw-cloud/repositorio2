"""Script placeholder para sembrar usuarios con roles."""
from app.models.user import users_db


def seed_users():
    # Implementar almacenamiento real (Alembic + SQLAlchemy) y encriptado.
    for username, user in users_db.items():
        print(f"Usuario disponible: {username} ({user.role})")


if __name__ == "__main__":
    seed_users()
