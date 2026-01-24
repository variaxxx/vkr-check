from dishka import FromDishka, Provider, Scope, provide
from fastapi import HTTPException, Request

from src.common.schemas import TokenUserInfo
from src.modules.auth.service import AuthService


class AuthGuardProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self, request: Request, auth_service: FromDishka[AuthService]
    ) -> TokenUserInfo:
        header = request.headers.get("authorization")

        if not header or not header.startswith("Bearer "):
            raise HTTPException(401, "No bearer token provided")

        token = header.replace("Bearer ", "")

        return auth_service.decode_jwt_token(token=token)
