from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
    )

    secret_key: str = Field("change-me-to-a-strong-secret")
    algorithm: str = Field("HS256")
    access_token_expire_minutes: int = Field(15)
    refresh_token_expire_days: int = Field(14)
    auth_code_expire_minutes: int = Field(10)
    refresh_cookie_name: str = Field("refresh_token")
    cookie_secure: bool = Field(False)
    cookie_samesite: str = Field("lax")
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://frontend:3000"])
    database_url: str = Field("sqlite:///./instagramproyect.db")
    frontend_origin: str = Field("http://localhost:3000")
    instagram_app_id: str = Field("")
    instagram_app_secret: str = Field("")
    instagram_callback_url: str = Field("http://localhost:8000/api/instagram/callback")
    instagram_graph_version: str = Field("v18.0")
    instagram_scopes_env: str = Field("", env="INSTAGRAM_SCOPES")

    @property
    def instagram_scopes(self) -> List[str]:
        if self.instagram_scopes_env:
            return [scope.strip() for scope in self.instagram_scopes_env.split(",") if scope.strip()]
        return [
            "instagram_graph_user_profile",
            "instagram_graph_user_media",
            "instagram_manage_comments",
        ]


settings = Settings()
