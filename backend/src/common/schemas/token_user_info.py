import uuid

from pydantic import BaseModel


class TokenUserInfo(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    roles: list[str]
