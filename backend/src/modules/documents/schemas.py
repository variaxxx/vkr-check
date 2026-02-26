import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ...infra.db.models import DocumentStatus


class DocumentAuthor(BaseModel):
    fio: str
    group: Optional[str]


class DocumentResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    processed_at: Optional[datetime]
    original_name: str
    status: DocumentStatus
    authors: Optional[List[DocumentAuthor]]
    topic: Optional[str]
    score: Optional[float]
    result: Optional[dict]


class DocumentShortResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    original_name: str
    status: DocumentStatus
    authors: Optional[List[DocumentAuthor]]
    topic: Optional[str]
    score: Optional[float]


class UploadDocumentResponse(BaseModel):
    skipped_count: int
    skipped_files: List[str]
