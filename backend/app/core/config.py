from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    secret_key: str = "change-me-to-a-strong-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    refresh_cookie_name: str = "refresh_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    allowed_origins: List[str] = ["http://localhost:3000", "http://frontend:3000"]
    database_url: str = "sqlite:///./instagramproyect.db"


settings = Settings()
