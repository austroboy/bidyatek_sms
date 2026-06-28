import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms.settings')

app = Celery('sms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()



# your_app/tasks.py
from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.files.storage import default_storage
import time

@shared_task
def generate_pdf_report_task(params):
    template = params['template']
    context = params['context']
    filename = params['filename']
    
    html_string = render_to_string(template, context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    file_path = f'reports/{filename}'
    default_storage.save(file_path, pdf)
    
    return file_path