# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms.settings')

# # Create the Celery application
# app = Celery('sms')

# # Use Django settings for Celery configuration
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Autodiscover tasks in each Django app
# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')


# sms/celery.py
from __future__ import absolute_import
import os
from celery import Celery
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms.settings')

app = Celery('sms')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Important addition
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')