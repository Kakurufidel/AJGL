from django.apps import AppConfig
from django.core.management import call_command

class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        # Crée un superuser automatiquement s'il n'existe pas
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(email='admin@ajgl.org').exists():
                User.objects.create_superuser(
                    email='admin@ajgl.org',
                    nom_complet='Admin AJGL',
                    telephone='+243000000000',
                    password='admin123'
                )
        except Exception:
            pass