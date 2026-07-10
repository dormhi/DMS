import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "dms_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Allow long-running tasks (6+ hour VOD downloads)
    task_soft_time_limit=None,
    task_time_limit=None,
    # Don't prefetch tasks — one long download shouldn't block the next
    worker_prefetch_multiplier=1,
)
