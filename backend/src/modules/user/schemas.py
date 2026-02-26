from typing import Union
from uuid import UUID

from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    id: Union[str, UUID]
    name: str
    email: str
