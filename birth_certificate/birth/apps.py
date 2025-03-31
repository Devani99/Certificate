from django.apps import AppConfig


class BirthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'birth'

    def ready(self):
        # Remove any model imports here to prevent double registration
        pass