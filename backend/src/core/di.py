from typing import AsyncGenerator

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.session import async_session_maker
from src.infra.minio import MinioProvider
from src.modules.auth.providers import AuthProvider
from src.modules.documents.providers import DocumentProvider
from src.modules.report.providers import ReportProvider
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

container = make_async_container(
    CoreProvider(),
    FastapiProvider(),
    AuthGuardProvider(),
    UserProvider(),
    DocumentProvider(),
    MinioProvider(),
    AuthProvider(),
    ReportProvider(),
)
