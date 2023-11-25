from datetime import timedelta
import os

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = None
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'


CELERY_BEAT_SCHEDULE = {
    'update_asset_prices_every_30_mins': {
        'task': 'myapp.tasks.update_asset_prices',  # Замените 'myapp' на название вашего Django-приложения
        'schedule': timedelta(minutes=30),
    },
}
