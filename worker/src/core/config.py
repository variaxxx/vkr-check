from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # connection params
    API_IP: str
    API_PORT: int

    # model params
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 8192    
    MODEL_NAME: str = "google/gemma-3n-E4B-it"
    EMBEDDINGS_MODEL: str = "intfloat/multilingual-e5-small"

    # rag
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    K_RETRIEVALS: int = 5

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
