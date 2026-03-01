from typing import Union
from uuid import UUID

from src.common.utils import normalize_uuid

from .repositories import UserRepository
from .schemas import UserInfoResponse


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create(
        self,
        user_id: Union[UUID, str],
        email: str,
        name: str,
    ):
        await self.repo.create_if_not_exists(
            user_id=user_id, email=email, name=name
        )

    async def get_by_id(
        self, id: Union[UUID, str]
    ) -> Union[UserInfoResponse, None]:
        id = normalize_uuid(id)
        user = await self.repo.get_by_id(id=id)
        return (
            UserInfoResponse(id=user.id, email=user.email, name=user.name)
            if user
            else user
        )
