import time
import uuid
from typing import Union

from celery import Celery

from src.common.enums import DocumentStatus
from src.common.utils import normalize_uuid
from src.core.config import settings
from src.infra.db.models import Document
from src.infra.db.session import sync_session_maker

worker = Celery(
    "ml_worker",
    broker=settings.CELERY_BROKER_URL,
    backend="rpc://",
)

worker.conf.update(
    # Формат сериализации задач
    task_serializer="json",
    # Принимаемые форматы данных
    accept_content=["json"],
    # Формат сериализации результатов
    result_serializer="json",
    # Часовой пояс
    timezone="Europe/Moscow",
    # Использовать UTC для внутренних операций
    enable_utc=True,
    # Максимальное время выполнения задачи (30 минут)
    task_time_limit=30 * 60,
    # Мягкий таймаут (25 минут)
    task_soft_time_limit=25 * 60,
    # Количество задач, которые воркер берёт одновременно
    worker_prefetch_multiplier=1,
    # Очередь по умолчанию
    task_default_queue="default",
    # Подтверждать выполнение задачи только после успешного завершения
    task_acks_late=True,
    # Не отключать ограничения скорости
    worker_disable_rate_limits=False,
    # Настройки логирования
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",  # noqa: E501
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",  # noqa: E501
)


@worker.task(bind=True)
def process_document(self, doc_id: Union[uuid.UUID, str]):
    with sync_session_maker() as session:
        doc_id = normalize_uuid(doc_id)

        doc = session.get(Document, doc_id)
        doc.status = DocumentStatus.IN_PROCESSING
        session.commit()

        time.sleep(30)

        doc.status = DocumentStatus.SUCCESS
        session.commit()
