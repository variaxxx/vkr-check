import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.enums import DocumentStatus
from src.infra.db.base import BaseModel

document_authors = Table(
    "document_authors",
    BaseModel.metadata,
    Column("document_id", ForeignKey("documents.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True),
)


class Document(BaseModel):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_url: Mapped[str] = mapped_column(
        String(length=512), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.UPLOADED
    )
    original_name: Mapped[str] = mapped_column(
        String(length=512), nullable=False
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    topic: Mapped[str] = mapped_column(String(), nullable=True)
    result: Mapped[dict] = mapped_column(JSONB, nullable=True)
    score: Mapped[float] = mapped_column(Numeric(4, 2), nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="documents")  # type: ignore # noqa: F821

    authors: Mapped[List["Author"]] = relationship(
        secondary=document_authors, back_populates="documents"
    )


class Author(BaseModel):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    last_name: Mapped[str] = mapped_column(String(256))
    first_name: Mapped[str] = mapped_column(String(256))
    middle_name: Mapped[str] = mapped_column(String(256), nullable=True)
    search_vector: Mapped[str] = mapped_column(TSVECTOR)

    documents: Mapped[List["Document"]] = relationship(
        secondary=document_authors, back_populates="authors"
    )


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)

    documents: Mapped[list["Document"]] = relationship(back_populates="user")  # type: ignore # noqa: F821
