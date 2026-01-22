from datetime import datetime, timedelta, timezone
from typing import Literal, Union
from uuid import UUID

import httpx
from cachetools import TTLCache, cached
from fastapi import HTTPException
from jose import JWTError, jwt

from src.core.config import Settings
from src.modules.user.service import UserService

from .schemas import TokenPayload, TokensResponse, TokenUserInfo

jwks_cache = TTLCache(maxsize=1, ttl=600)


class AuthService:
    def __init__(self, user_service: UserService, config: Settings):
        self.user_service = user_service
        self.config = config
        self.JWKS_URL = (
            f"{'http' if config.DEBUG else 'https'}://{config.KEYCLOACK_HOST}/"
            f"{'auth/' if config.KEYCLOACK_USES_AUTH_ENDPOINT else ''}"
            f"realms/{config.KEYCLOACK_REALM}/protocol/openid-connect/certs"
        )

    async def login(self, token: str) -> TokensResponse:
        try:
            header = jwt.get_unverified_header(token)
            kid = header["kid"]
            jwks = self.get_jwks()

            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if key is None:
                raise HTTPException(401, "Invalid token")

            payload = jwt.decode(
                token, key, algorithms=["RS256"], audience="account"
            )
        except JWTError:
            raise HTTPException(401, "Invalid token")

        roles = payload["realm_access"]["roles"]
        if not any(x in self.config.KEYCLOACK_ALLOWED_ROLES for x in roles):
            raise HTTPException(403, "Forbidden")

        user_id = payload["sub"]
        await self.user_service.create(
            user_id=user_id,
            email=payload["email"],
            name=payload["name"],
        )

        return TokensResponse(
            access_token=self.create_jwt_token(user_id=user_id),
            refresh_token=self.create_jwt_token(
                user_id=user_id, type="refresh"
            ),
        )

    def refresh_token(self, refresh_token: str) -> str:
        user = self.decode_jwt_token(token=refresh_token, type="refresh")
        return self.create_jwt_token(user_id=user.id)

    def create_jwt_token(
        self,
        user_id: Union[str, UUID],
        type: Literal["access", "refresh"] = "access",
    ) -> str:
        age_mins = (
            self.config.ACCESS_TOKEN_EXPIRE_MINUTES
            if type == "access"
            else self.config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
        )
        secret = (
            self.config.JWT_ACCESS_SECRET
            if type == "access"
            else self.config.JWT_REFRESH_SECRET
        )

        payload: TokenPayload = {
            "user": {"id": user_id},
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=age_mins),
        }
        return jwt.encode(
            payload,
            secret,
            algorithm=self.config.JWT_ALGORITHM,
        )

    def decode_jwt_token(
        self, token: str, type: Literal["access", "refresh"] = "access"
    ) -> TokenUserInfo:
        try:
            secret = (
                self.config.JWT_ACCESS_SECRET
                if type == "access"
                else self.config.JWT_REFRESH_SECRET
            )
            payload: TokenPayload = jwt.decode(
                token=token,
                key=secret,
                algorithms=[self.config.JWT_ALGORITHM],
            )
            return TokenUserInfo.model_validate(payload.get("user"))
        except JWTError:
            raise HTTPException(401, "Invalid token")

    @cached(jwks_cache)
    def get_jwks(self):
        response = httpx.get(self.JWKS_URL)
        response.raise_for_status()
        return response.json()
