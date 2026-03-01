from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    secret_key: str = "change-me-to-a-strong-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    refresh_cookie_name: str = "refresh_token"
    access_cookie_name: str = "access_token"
    cookie_secure: bool = True
    cookie_samesite: str = "lax"
    allowed_origins: List[str] = ["http://localhost:3000"]


settings = Settings()
