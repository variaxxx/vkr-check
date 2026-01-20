import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.utils import normalize_uuid
from src.infra.db.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, sub: uuid.UUID | str, email: str, name: str) -> User:
        user_id = normalize_uuid(sub)

        new_user = User(id=user_id, email=email, name=name)

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        query = select(User).where(User.id == id)
        result = await self.db.execute(query)
        return result.scalars().one_or_none()

    async def create_if_not_exists(
        self, sub: uuid.UUID | str, email: str, name: str
    ) -> User:
        user_id = normalize_uuid(sub)

        select_user_query = select(User).where(User.id == user_id)
        result = await self.db.execute(select_user_query)
        db_user = result.scalars().first()

        if not db_user:
            db_user = User(id=user_id, email=email, name=name)
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

        return db_user
