from celery import Celery

from src.core.config import settings

worker = Celery(
    "ml_worker",
    broker=settings.CELERY_BROKER_URL,
    backend="rpc://",
    include=["src.tasks.process_document"],
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
    worker_concurrency=1,
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

