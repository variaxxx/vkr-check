from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Для локального запуска используем `.env`, а при его отсутствии берем `.env.production`.
    model_config = SettingsConfigDict(env_file=(".env", ".env.production"))

    # connection params
    API_IP: str
    API_PORT: int

    # model params
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 8192
    MODEL_NAME: str = "hf.co/unsloth/gemma-3n-E4B-it-GGUF:Q4_K_XL"
    EMBEDDINGS_MODEL: str = "intfloat/multilingual-e5-small"

    # google drive api params
    SCOPES: str
    SERVICE_ACCOUT_FILE: str
    PARENT_FOLDER_ID: str
    OAUTH_CLIENT_FILE: str


    # rag
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    K_RETRIEVALS: int = 10

    # celery
    CELERY_BROKER_URL: str

    # db
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # minio
    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str


settings = Settings()
