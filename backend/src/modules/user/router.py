from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.common.schemas import TokenUserInfo
from src.modules.user.schemas import UserInfoResponse

from .service import UserService

router = APIRouter(prefix="/user", tags=["User"], route_class=DishkaRoute)


@router.get("/me", response_model=UserInfoResponse)
async def get_me(
    user: FromDishka[TokenUserInfo], user_service: FromDishka[UserService]
) -> UserInfoResponse:
    return await user_service.get_by_id(id=user.id)
