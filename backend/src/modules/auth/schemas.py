from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel

from src.common.schemas import TokenUserInfo


class KCAuthRequest(BaseModel):
    token: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str


class TokenPayload(TypedDict):
    user: TokenUserInfo
    iat: datetime
    exp: datetime
