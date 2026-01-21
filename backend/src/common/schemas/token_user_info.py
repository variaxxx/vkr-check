from pydantic import BaseModel


class TokenUserInfo(BaseModel):
    id: str
