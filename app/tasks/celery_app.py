from celery import Celery
from app.config import settings

celery_app = Celery(
    'attendance',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.ocr_tasks',
        'app.tasks.validation_tasks',
        'app.tasks.export_tasks',
    ]
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Africa/Kigali',
    task_routes={
        'app.tasks.ocr_tasks.*': {'queue': 'ocr'},
        'app.tasks.validation_tasks.*': {'queue': 'validation'},
        'app.tasks.export_tasks.*': {'queue': 'export'},
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
