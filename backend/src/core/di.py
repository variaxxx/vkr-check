from typing import AsyncGenerator

from dishka import Provider, Scope, make_async_container, provide
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.session import async_session_maker
from src.infra.minio import MinioProvider
from src.modules.auth.providers import AuthProvider
from src.modules.documents.providers import DocumentProvider
from src.modules.user.providers import UserProvider

from .auth import AuthGuardProvider
from .config import Settings, settings


class CoreProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Settings:
        return settings

    @provide(scope=Scope.REQUEST)
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_request(self) -> Request:
        raise NotImplementedError()


container = make_async_container(
    CoreProvider(),
    AuthGuardProvider(),
    UserProvider(),
    DocumentProvider(),
    MinioProvider(),
    AuthProvider(),
)
