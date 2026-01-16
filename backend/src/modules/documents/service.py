import uuid
from typing import List

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import S3Error
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.schemas import FindManyResponse, TokenUserInfo
from src.common.utils import clamp
from src.infra.db.models import Document, DocumentStatus
from src.infra.minio import MinioService
from src.modules.user.repositories import UserRepository

from .repositories import DocumentRepository
from .schemas import DocumentInfo


class DocumentService:
    def __init__(
        self,
        doc_repo: DocumentRepository,
        user_repo: UserRepository,
        minio: MinioService,
        db: AsyncSession,
    ):
        self.doc_repo = doc_repo
        self.user_repo = user_repo
        self.minio = minio
        self.db = db

    async def upload(
        self, files: list[UploadFile], user: TokenUserInfo
    ) -> List[DocumentInfo]:
        ALLOWED_FILE_TYPES = [
            # .docx
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            # ,pdf
            "application/pdf",
        ]
        uploaded_docs = []

        await self.user_repo.create_if_not_exists(
            sub=user.id, email=user.email, name=user.name
        )

        for file in files:
            # TODO: skipped count
            if file.content_type not in ALLOWED_FILE_TYPES:
                continue

            object_name = f"{uuid.uuid4()}-{file.filename}"

            self.minio.client.put_object(
                bucket_name="documents",
                object_name=object_name,
                data=file.file,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=file.content_type,
            )

            new_doc = Document(
                file_url=f"documents/{object_name}",
                original_name=file.filename,
                user_id=user.id,
            )
            self.db.add(new_doc)
            uploaded_docs.append(new_doc)

        await self.db.commit()

        result = []
        for doc in uploaded_docs:
            await self.db.refresh(doc)

            # TODO: push event to RMQ

            result.append(
                DocumentInfo(
                    id=doc.id,
                    created_at=doc.created_at,
                    processed_at=None,
                    status=DocumentStatus.UPLOADED,
                    authors=None,
                    result=None,
                    original_name=doc.original_name,
                )
            )

        return result

    async def download(
        self,
        document_id: uuid.UUID,
        user: TokenUserInfo,
    ) -> StreamingResponse:
        try:
            document = await self.doc_repo.get_by_id(id=document_id)

            if document is None or document.user_id != user.id:
                raise HTTPException(404, "Document not found")

            bucket_name = document.file_url.split("/")[0]
            object_name = document.file_url[len(bucket_name) + 1 :]

            response = self.minio.client.get_object(
                bucket_name=bucket_name, object_name=object_name
            )

            headers = {}
            if hasattr(response, "headers"):
                content_type = response.headers.get("content-type")
                if content_type:
                    headers["Content-Type"] = content_type

            return StreamingResponse(
                response.stream(amt=1024 * 1024),
                media_type=headers.get(
                    "Content-Type", "application/octet-stream"
                ),
            )
        except S3Error:
            raise HTTPException(404, "File not found")

    async def get_by_id(
        self,
        document_id: uuid.UUID | str,
        user: TokenUserInfo,
    ) -> DocumentInfo:
        doc = await self.doc_repo.get_by_id(id=document_id)

        if doc is None or doc.user_id != user.id:
            raise HTTPException(404, "Document not found")

        return DocumentInfo.model_validate(
            {**doc.to_dict(), "authors": None, "result": None},
        )

    async def get_many(
        self,
        user: TokenUserInfo,
        offset: int = 0,
        limit: int = 25,
    ) -> FindManyResponse[DocumentInfo]:
        limit = clamp(limit, 0, 50)
        offset = max(0, offset)

        docs = await self.doc_repo.get_many(
            limit=limit, offset=offset, user_id=user.id
        )

        formatted_docs = list(
            map(
                lambda doc: DocumentInfo.model_validate(
                    {**doc.to_dict(), "authors": None, "result": None},
                ),
                docs,
            )
        )

        # TODO: total
        return FindManyResponse[DocumentInfo](
            total=5, count=len(formatted_docs), items=formatted_docs
        )
