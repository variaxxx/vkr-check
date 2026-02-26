import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.enums import DocumentStatus
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
        query = (
            select(Document)
            .where(Document.id == id)
            .options(selectinload(Document.authors))
        )
        result = await self.db.execute(query)
        return result.scalars().one_or_none()

    async def get_many(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        user_id: Optional[uuid.UUID] = None,
        status: Optional[DocumentStatus] = None,
    ) -> List[Document]:
        where = []

        if user_id is not None:
            where.append(Document.user_id == user_id)
        if status is not None:
            where.append(Document.status == status)

        query = (
            select(Document)
            .options(selectinload(Document.authors))
            .order_by(desc(Document.created_at))
        )

        if where:
            query = query.where(and_(*where))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all_processed(
        self,
        user_id: Optional[uuid.UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Document]:
        where = [
            Document.status.in_(
                [DocumentStatus.APPROVED, DocumentStatus.REJECTED]
            ),
        ]

        if user_id is not None:
            where.append(Document.user_id == user_id)
        if from_date is not None:
            where.append(Document.created_at >= from_date)
        if to_date is not None:
            where.append(Document.created_at <= to_date)

        query = (
            select(Document)
            .options(selectinload(Document.authors))
            .order_by(desc(Document.created_at))
            .where(and_(*where))
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_total(
        self,
        user_id: Optional[uuid.UUID] = None,
        status: Optional[DocumentStatus] = None,
    ) -> int:
        where = []

        if user_id is not None:
            where.append(Document.user_id == user_id)
        if status is not None:
            where.append(Document.status == status)

        query = select(func.count()).select_from(Document)

        if where:
            query = query.where(and_(*where))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def search(
        self,
        query: str,
        limit: int,
        offset: int,
        user_id: uuid.UUID,
        status: Optional[DocumentStatus] = None,
    ) -> List[Document]:
        results = await self.db.execute(
            text("""
                WITH matching_docs AS (
                    SELECT
                        d.id,
                        MAX(
                            ts_rank_cd(
                                a.search_vector,
                                websearch_to_tsquery('russian', :query)
                            )
                        ) as rank
                    FROM authors a
                    JOIN document_authors da ON da.author_id = a.id
                    JOIN documents d ON da.document_id = d.id
                    WHERE (
                        search_vector @@ websearch_to_tsquery('russian', :query)
                        OR (
                            a.last_name || ' ' || a.first_name || ' ' || coalesce(a.middle_name, '') || ' ' || coalesce(a."group", '')
                        ) % :query
                        OR a."group" ILIKE '%' || :query || '%'
                    )
                    AND d.user_id = :user_id
                    AND d.status = coalesce(:status, d.status)
                    GROUP BY d.id
                )
                SELECT
                    d.*,
                    array_agg(
                        jsonb_build_object(
                            'first_name', a.first_name,
                            'last_name', a.last_name,
                            'middle_name', a.middle_name,
                            'group', a.group
                        )
                        ORDER BY a.last_name
                    ) as authors
                FROM matching_docs md
                JOIN documents d ON d.id = md.id
                JOIN document_authors da ON da.document_id = d.id
                JOIN authors a ON a.id = da.author_id
                GROUP BY d.id, md.rank
                ORDER BY rank DESC
                OFFSET :offset
                LIMIT :limit;
            """),  # noqa: E501
            {
                "query": query,
                "user_id": user_id,
                "limit": limit,
                "offset": offset,
                "status": status.name if status else None,
            },
        )

        return results.all()

    async def search_total(
        self,
        query: str,
        user_id: uuid.UUID,
        status: Optional[DocumentStatus] = None,
    ) -> int:
        result = await self.db.execute(
            text("""
                SELECT COUNT(DISTINCT d.id) as cnt
                FROM authors a
                JOIN document_authors da ON da.author_id = a.id
                JOIN documents d ON da.document_id = d.id
                WHERE (
                    search_vector @@ websearch_to_tsquery('russian', :query)
                    OR (
                        a.last_name || ' ' || a.first_name || ' ' || coalesce(a.middle_name, '') || ' ' || coalesce(a."group", '')
                    ) % :query
                    OR a."group" ILIKE '%' || :query || '%'
                )
                AND d.user_id = :user_id
                AND d.status = coalesce(:status, d.status)
            """),  # noqa: E501
            {
                "query": query,
                "user_id": user_id,
                "status": status.name if status else None,
            },
        )

        return result.scalar_one()
