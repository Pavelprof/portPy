import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portpy.settings')

app = Celery('portpy')

app.config_from_object('portpy.celery_config')
app.conf.beat_max_loop_interval = 30

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')