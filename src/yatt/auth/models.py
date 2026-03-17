from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    type: str


class AccessToken(BaseModel):
    sub: str
    exp: datetime
    scopes: list[str]
