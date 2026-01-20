from dishka import FromDishka, Provider, Scope, provide
from fastapi import Request

from src.common.schemas import TokenUserInfo
from src.modules.auth.service import AuthService


class AuthGuardProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self, request: Request, auth_service: FromDishka[AuthService]
    ) -> TokenUserInfo:
        token = request.cookies.get("access_token")
        return auth_service.decode_jwt_token(token=token)
