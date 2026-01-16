import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.utils import normalize_uuid
from src.infra.db.models import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, file_url: str, user_id: uuid.UUID | str) -> Document:
        user_id = normalize_uuid(user_id)
        new_document = Document(file_url=file_url, user_id=user_id)

        self.db.add(new_document)
        await self.db.commit()
        await self.db.refresh(new_document)

        return new_document

    async def get_by_id(self, id: uuid.UUID | str) -> Document | None:
        id = normalize_uuid(id)
        query = select(Document).where(Document.id == id)
        result = await self.db.execute(query)
        return result.scalars().one_or_none()

    async def get_many(
        self,
        limit: Optional[int],
        offset: Optional[int],
        user_id: Optional[uuid.UUID],
    ) -> List[Document]:
        query = (
            select(Document)
            .limit(limit)
            .offset(offset)
            .where(Document.user_id == user_id if user_id else True)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
