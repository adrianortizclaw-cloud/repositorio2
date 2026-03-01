from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY", default="change-me-to-a-strong-secret")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    refresh_cookie_name: str = "refresh_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    database_url: str = Field(default="sqlite:///./instagramproyect.db", env="DATABASE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
