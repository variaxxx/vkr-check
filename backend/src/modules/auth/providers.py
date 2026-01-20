from dishka import Provider, Scope, provide

from .service import AuthService


class AuthProvider(Provider):
    # @provide(scope=Scope.REQUEST)
    # def get_auth_repo(self, session: AsyncSession) -> DocumentRepository:
    #     return DocumentRepository(session)

    auth_service = provide(AuthService, scope=Scope.REQUEST)
