import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ...infra.db.models import DocumentStatus


class DocumentInfo(BaseModel):
    id: uuid.UUID
    created_at: datetime
    processed_at: Optional[datetime]
    original_name: str
    status: DocumentStatus
    authors: Optional[List[str]]
    result: Optional[str]


class UploadDocumentResponse(BaseModel):
    skipped_count: int
