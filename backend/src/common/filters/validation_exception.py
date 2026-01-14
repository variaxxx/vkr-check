from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = []

    for err in exc.errors():
        loc = ".".join(str(x) for x in err["loc"] if x != "body")
        errors.append({"field": loc or None, "message": err["msg"]})

    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "message": "Validation failed",
            "errors": errors,
        },
    )
