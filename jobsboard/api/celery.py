# jobsboard/api/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

# Load settings from Django settings, prefixed with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed apps
app.autodiscover_tasks()

# Optional: Example periodic task schedule
app.conf.beat_schedule = {
    'example-task-every-hour': {
        'task': 'jobsboard.payments.tasks.send_payment_reminder_email',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
