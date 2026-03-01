from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    username: str
    role: str = "guest"
    token_type: str = "access"
    jti: Optional[str] = None
