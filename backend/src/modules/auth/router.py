from typing import Literal

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Request, Response

from src.core.config import settings

from .schemas import AccessTokenResponse, KCAuthRequest
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@router.post("/kc", response_model=AccessTokenResponse)
async def kc_auth(
    body: KCAuthRequest,
    auth_service: FromDishka[AuthService],
    response: Response,
):
    tokens = await auth_service.login(token=body.token)
    set_token_cookie(
        response=response, token_type="refresh", value=tokens.refresh_token
    )
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    request: Request,
    response: Response,
    auth_service: FromDishka[AuthService],
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(401, "No token provided")

    access_token = auth_service.refresh_token(refresh_token=refresh_token)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token", path="/")


def set_token_cookie(
    response: Response, token_type: Literal["access", "refresh"], value: str
):
    if token_type == "access":
        max_age = 60 * settings.ACCESS_TOKEN_EXPIRE_MINUTES
    else:
        max_age = (60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,)

    response.set_cookie(
        key=f"{token_type}_token",
        value=value,
        httponly=True,
        samesite="strict",
        path="/",
        max_age=max_age,
        secure=settings.ENV == "prod",
    )
