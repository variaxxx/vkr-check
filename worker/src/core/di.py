from dishka import Provider, Scope, make_container, provide
from sqlalchemy.orm import Session

from src.core.config import Settings, settings
from src.infra.db.session import sync_session_maker
from src.infra.minio.provider import MinioProvider
from src.services.provider import ServicesProvider


def run_in_di(fn):
    def wrapper(*args, **kwargs):
        with container(scope=Scope.REQUEST) as di:
            return fn(di, *args, **kwargs)

    return wrapper


class CoreProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Settings:
        return settings

    @provide(scope=Scope.REQUEST)
    def get_db_session(self) -> Session:
        session = sync_session_maker()
        return session


container = make_container(
    CoreProvider(),
    MinioProvider(),
    ServicesProvider(),
)
