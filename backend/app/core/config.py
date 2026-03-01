from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    secret_key: str = Field("change-me-to-a-strong-secret", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(14, env="REFRESH_TOKEN_EXPIRE_DAYS")
    auth_code_expire_minutes: int = Field(10, env="AUTH_CODE_EXPIRE_MINUTES")
    refresh_cookie_name: str = Field("refresh_token", env="REFRESH_COOKIE_NAME")
    cookie_secure: bool = Field(False, env="COOKIE_SECURE")
    cookie_samesite: str = Field("lax", env="COOKIE_SAMESITE")
    allowed_origins: List[str] = Field(["http://localhost:3000", "http://frontend:3000"], env="ALLOWED_ORIGINS")
    database_url: str = Field("sqlite:///./instagramproyect.db", env="DATABASE_URL")
    frontend_origin: str = Field("http://localhost:3000", env="FRONTEND_ORIGIN")
    instagram_app_id: str = Field("", env="INSTAGRAM_APP_ID")
    instagram_app_secret: str = Field("", env="INSTAGRAM_APP_SECRET")
    instagram_callback_url: str = Field("http://localhost:8000/api/instagram/callback", env="INSTAGRAM_CALLBACK_URL")
    instagram_graph_version: str = Field("v18.0", env="INSTAGRAM_GRAPH_VERSION")
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
