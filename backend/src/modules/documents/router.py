import uuid
from typing import Annotated, Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.common.enums import DocumentStatus
from src.common.schemas import FindManyResponse, TokenUserInfo

from .schemas import (
    DocumentResponse,
    DocumentShortResponse,
    UploadDocumentResponse,
)
from .service import DocumentService

router = APIRouter(
    prefix="/documents", tags=["Processing"], route_class=DishkaRoute
)


@router.post("/upload", response_model=UploadDocumentResponse, status_code=201)
async def upload(
    document_service: FromDishka[DocumentService],
    user: FromDishka[TokenUserInfo],
    files: Annotated[list[UploadFile], File(...)],
) -> UploadDocumentResponse:
    if not files:
        raise HTTPException(401, "No files provided")

    return await document_service.upload(files=files, user=user)


@router.get("", response_model=FindManyResponse[DocumentShortResponse])
async def get_documents(
    document_service: FromDishka[DocumentService],
    user: FromDishka[TokenUserInfo],
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    status: Optional[DocumentStatus] = None,
) -> FindManyResponse[DocumentShortResponse]:
    return await document_service.get_many(
        offset=offset, limit=limit, user=user, status=status
    )


@router.get("/search", response_model=FindManyResponse[DocumentShortResponse])
async def search_document(
    query: str,
    document_service: FromDishka[DocumentService],
    user: FromDishka[TokenUserInfo],
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> FindManyResponse[DocumentShortResponse]:
    return await document_service.search(
        query=query, user=user, limit=limit, offset=offset
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_by_id(
    document_id: str,
    document_service: FromDishka[DocumentService],
    user: FromDishka[TokenUserInfo],
) -> DocumentResponse:
    return await document_service.get_by_id(document_id=document_id, user=user)


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    document_service: FromDishka[DocumentService],
    user: FromDishka[TokenUserInfo],
) -> StreamingResponse:
    return await document_service.download(document_id=document_id, user=user)
