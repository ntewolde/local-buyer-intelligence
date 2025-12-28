"""
Celery Configuration for Background Tasks
"""
import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "local_buyer_intelligence",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Check for eager mode (for testing)
task_always_eager = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
task_eager_propagates = os.environ.get("CELERY_TASK_EAGER_PROPAGATES", "false").lower() == "true"

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    task_always_eager=task_always_eager,
    task_eager_propagates=task_eager_propagates,
)






