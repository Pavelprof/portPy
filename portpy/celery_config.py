from datetime import timedelta
import os

broker_url = os.environ.get('broker_url', 'redis://localhost:6379/1')
result_backend = 'django-db'
cache_backend = 'default'
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'UTC'
broker_connection_retry_on_startup = True

# beat_schedule = django_celery_beat.schedulers:DatabaseScheduler # turn it on if you want to use django_celery_beat with your admin

beat_schedule = {
    'update_asset_prices_every_60_mins': {
        'task': 'portfolio.tasks.update_asset_prices',
        'schedule': timedelta(minutes=60),
    },
}