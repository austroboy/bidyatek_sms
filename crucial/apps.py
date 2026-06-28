from django.apps import AppConfig


class CrucialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crucial'

    def ready(self):
        import crucial.signals

