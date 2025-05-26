import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecowiser.settings')

app = Celery('ecowiser')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    print('This is a debug task running in Celery.')
    # You can add more debug information or logic here if needed.