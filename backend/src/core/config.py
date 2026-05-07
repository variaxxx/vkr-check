from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str

    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://127.0.0.1:4200",
        "http://localhost:4200",
    ]

    KC_HOST: str
    KC_USES_AUTH_ENDPOINT: bool = True
    KC_REALM: str
    KC_ALLOWED_ROLES: list[str] = []

    CELERY_BROKER_URL: str

    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    ENV: Literal["prod", "dev"] = "dev"


settings = Settings()
