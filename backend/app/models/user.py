from dataclasses import dataclass
from typing import Dict, Optional

from pydantic import BaseModel


database_users: Dict[str, Dict] = {
    "client@example.com": {
        "username": "client@example.com",
        "full_name": "Cliente Instagram",
        "role": "client",
        "hashed_password": "$2b$12$y3n0nWb9WcItE9zUvFaH7uuzh2Q3a2b8N7y.9eNk8KjRjA/LoGm8.",
        "disabled": False
    },
    "admin@example.com": {
        "username": "admin@example.com",
        "full_name": "Admin Instagram",
        "role": "admin",
        "hashed_password": "$2b$12$y3n0nWb9WcItE9zUvFaH7uuzh2Q3a2b8N7y.9eNk8KjRjA/LoGm8.",
        "disabled": False
    }
}


class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "client"
    disabled: bool = False


@dataclass
class UserInDB(User):
    hashed_password: str


class TokenPayload(BaseModel):
    username: str
    role: str = "guest"


users_db: Dict[str, UserInDB] = {
    username: UserInDB(**data) for username, data in database_users.items()
}
