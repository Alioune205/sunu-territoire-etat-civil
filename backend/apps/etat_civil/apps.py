from django.apps import AppConfig

class EtatCivilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.etat_civil'
    verbose_name = 'Gestion Avancée de l\'État Civil'

    def ready(self):
        # Import des signaux une fois l'application chargée
        try:
            import apps.etat_civil.signals_attribution  # noqa
        except ImportError:
            pass
