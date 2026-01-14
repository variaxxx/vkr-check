from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

# from src.core.security import decode_jwt
# from src.schemas.auth import TokenUserInfo
from src.infra.db.session import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# def auth_guard(request: Request) -> TokenUserInfo:
#     token = extract_bearer_token(request)
#     payload = decode_jwt(token)
#     return TokenUserInfo.model_validate(payload.get("user"))


# async def socket_auth_guard(websocket: WebSocket) -> str:
#     header = websocket.headers.get("authorization")
#     if not header or not header.startswith("Bearer "):
#         await websocket_manager.send_error("Invalid token", websocket)

#     token = header.split()[1]
#     payload = decode_jwt(token)
#     return TokenUserInfo.model_validate(payload.get("user"))


# def extract_bearer_token(request: Request) -> str:
#     header = request.headers.get("authorization")
#     if not header or not header.startswith("Bearer "):
#         raise HTTPException(401, "Unauthorized")

#     token = header.split()[1]
#     return token
