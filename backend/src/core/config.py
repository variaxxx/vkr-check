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

    KEYCLOACK_HOST: str
    KEYCLOACK_USES_AUTH_ENDPOINT: bool = True
    KEYCLOACK_REALM: str
    KEYCLOACK_ALLOWED_ROLES: list[str] = []

    CELERY_BROKER_URL: str

    DEBUG: bool = False


settings = Settings()
