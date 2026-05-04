from django.apps import AppConfig
from django.core.management import call_command
import os

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        # Exécuter les migrations automatiquement au démarrage
        from django.core.management import call_command
        import sys
        
        # Éviter les erreurs lors des collectstatic
        if 'migrate' not in sys.argv and 'collectstatic' not in sys.argv:
            try:
                call_command('migrate', interactive=False)
                print("✅ Migrations appliquées automatiquement")
            except Exception as e:
                print(f"⚠️ Erreur migrations: {e}")
        
        # Créer un superutilisateur automatiquement s'il n'existe pas
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
                print("✅ Superutilisateur créé: admin@ajgl.org / admin123")
        except Exception as e:
            print(f"⚠️ Erreur création superuser: {e}")