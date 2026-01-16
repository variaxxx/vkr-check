from dishka import FromDishka, Provider, Scope, provide
from fastapi import HTTPException, Request

from src.common.schemas.token_user_info import TokenUserInfo
from src.modules.user.service import UserService


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self, request: Request, user_service: FromDishka[UserService]
    ) -> TokenUserInfo:
        header = request.headers.get("authorization")
        if not header or not header.startswith("Bearer "):
            raise HTTPException(401, "Unauthorized")

        token = header.split()[1]
        token_payload = await user_service.validate_access_token(token=token)
        if token_payload is None:
            raise HTTPException(401, "Unauthorized")

        return token_payload
