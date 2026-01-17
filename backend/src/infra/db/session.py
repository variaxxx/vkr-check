from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

DATABASE_URL_ASYNC = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
DATABASE_URL_SYNC = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(
    DATABASE_URL_ASYNC,
)

engine_sync = create_engine(DATABASE_URL_SYNC)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
)

sync_session_maker = sessionmaker(engine_sync)
