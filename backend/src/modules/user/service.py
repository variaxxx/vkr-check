import httpx
from cachetools import TTLCache, cached
from jose import JWTError, jwt

from src.common.schemas import TokenUserInfo
from src.core.config import Settings

from .repositories import UserRepository

jwks_cache = TTLCache(maxsize=1, ttl=600)


class UserService:
    def __init__(self, repo: UserRepository, config: Settings):
        self.repo = repo
        self.config = config
        self.JWKS_URL = (
            f"{'http' if config.DEBUG else 'https'}://{config.KEYCLOACK_HOST}/"
            f"{'auth/' if config.KEYCLOACK_USES_AUTH_ENDPOINT else ''}"
            f"realms/{config.KEYCLOACK_REALM}/protocol/openid-connect/certs"
        )

    async def validate_access_token(self, token: str) -> TokenUserInfo | None:
        try:
            header = jwt.get_unverified_header(token)
            kid = header["kid"]
            jwks = self.get_jwks()
            key = next(k for k in jwks["keys"] if k["kid"] == kid)
            payload = jwt.decode(
                token, key, algorithms=["RS256"], audience="account"
            )

            roles = payload["realm_access"]["roles"]
            if any(x in self.config.KEYCLOACK_ALLOWED_ROLES for x in roles):
                return TokenUserInfo(
                    id=payload["sub"],
                    email=payload["email"],
                    name=payload["name"],
                    roles=roles,
                )
            return None
        except JWTError as e:
            print(e)
            return None

    @cached(jwks_cache)
    def get_jwks(self):
        response = httpx.get(self.JWKS_URL)
        response.raise_for_status()
        return response.json()
