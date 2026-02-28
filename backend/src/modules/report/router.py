from datetime import datetime

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.common.schemas.token_user_info import TokenUserInfo
from src.modules.report.service import ReportService

router = APIRouter(prefix="/report", tags=["Report"], route_class=DishkaRoute)


@router.get("")
async def get_report_for_all(
    report_service: FromDishka[ReportService],
    user: FromDishka[TokenUserInfo],
    start: datetime = Query(...),
    end: datetime = Query(...),
) -> StreamingResponse:
    return await report_service.get_for_all(user=user, start=start, end=end)
