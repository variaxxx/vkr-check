from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .repositories import UserRepository
from .service import UserService


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    user_service = provide(UserService, scope=Scope.REQUEST)
