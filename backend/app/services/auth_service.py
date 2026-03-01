from typing import Optional

from ..models.user import users_db, UserInDB


def get_user(username: str) -> Optional[UserInDB]:
    return users_db.get(username)
