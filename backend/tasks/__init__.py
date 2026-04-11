from celery import Celery
from celery.schedules import crontab

from backend.config import settings

celery_app = Celery(
    "intel_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "daily-push-every-hour": {
        "task": "backend.tasks.daily_push.run_hourly_push",
        "schedule": crontab(minute=0),
    },
    "daily-free-credits-reset": {
        "task": "backend.tasks.daily_free_credits.reset_daily_free_credits",
        "schedule": crontab(hour=0, minute=0),
    },
}

celery_app.autodiscover_tasks(["backend.tasks"])
