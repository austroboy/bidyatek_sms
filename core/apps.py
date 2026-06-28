from django.apps import AppConfig
from django.db.models.signals import post_migrate
from datetime import datetime

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.models import Admission_Year  # Import your model
        from django.db import connection

        # Define a function to create the Admission_Year instance
        def create_default_admission_year(sender, **kwargs):
            if 'core_admission_year' in connection.introspection.table_names():
                current_year = str(datetime.now().year)
                Admission_Year.objects.get_or_create(name=current_year)

        post_migrate.connect(create_default_admission_year, sender=self)
