from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str

    # MINIO_PORT: int
    # MINIO_PANEL_PORT: int
    # MINIO_ACCESS_KEY: str
    # MINIO_SECRET_KEY: str
    # MINIO_HOST: str

    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://127.0.0.1:4200",
        "http://localhost:4200",
    ]
    # ASSETS_BUCKET_NAME: str = "assets"


settings = Settings()
