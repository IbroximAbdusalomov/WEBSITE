# celery.py

import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

app = Celery('root')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'decrease_top_duration': {
        'task': 'films.tasks.decrease_top_duration',  # Изменено с 'myapp.tasks' на 'films.tasks'
        'schedule': timedelta(seconds=20),  # Уменьшать top_duration каждые 20 секунд
    },
}

app.autodiscover_tasks()