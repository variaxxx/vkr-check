from dishka import Provider, Scope, provide

from .service import MinioService


class MinioProvider(Provider):
    minio_service = provide(MinioService, scope=Scope.APP)
