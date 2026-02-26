from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

DATABASE_URL_SYNC = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


engine_sync = create_engine(DATABASE_URL_SYNC)

sync_session_maker = sessionmaker(engine_sync)
