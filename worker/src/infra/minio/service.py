from minio import Minio
from src.core.config import Settings


class MinioService:
    def __init__(self, config: Settings):
        self.config = config
        self.client = None
        self.document_bucket = "documents"

        self._init_client()
        self._ensure_bucket_exists()

    def _init_client(self) -> None:
        self.client = Minio(
            endpoint=f"{self.config.MINIO_HOST}:{self.config.MINIO_PORT}",
            access_key=self.config.MINIO_ACCESS_KEY,
            secret_key=self.config.MINIO_SECRET_KEY,
            secure=False,
        )

    def _ensure_bucket_exists(self) -> None:
        if not self.client.bucket_exists(self.document_bucket):
            self.client.make_bucket(self.document_bucket)
