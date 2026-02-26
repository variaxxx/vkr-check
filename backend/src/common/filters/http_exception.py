from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.common.schemas import ResponseStructure


async def http_exception_handler(request: Request, exc: HTTPException):
    content = ResponseStructure(
        status=exc.status_code, message=exc.detail, data=None
    ).model_dump()
    return JSONResponse(
        content=content,
        status_code=exc.status_code,
        headers=exc.headers or None,
    )
