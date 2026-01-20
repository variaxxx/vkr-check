from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .repositories import DocumentRepository
from .service import DocumentService


class DocumentProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> DocumentRepository:
        return DocumentRepository(session)

    user_service = provide(DocumentService, scope=Scope.REQUEST)
