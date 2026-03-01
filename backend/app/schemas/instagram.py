from datetime import datetime

from pydantic import BaseModel


class InstagramLoginUrlResponse(BaseModel):
    url: str
    state: str | None = None


class InstagramSessionResponse(BaseModel):
    session_id: str
    ig_user_id: str
    username: str | None = None
    name: str | None = None
    created_at: datetime


__all__ = ["InstagramLoginUrlResponse", "InstagramSessionResponse"]
