from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("")
async def healthcheck():
    return {"status": "OK"}
