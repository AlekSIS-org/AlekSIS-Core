from django.apps import AppConfig, apps
from django.db.models.signals import post_save

from .signals import clean_scss


class CoreConfig(AppConfig):
    name = 'biscuit.core'
    verbose_name = 'BiscuIT - The Free School Information System'

    def ready(self) -> None:
        clean_scss()
        post_save.connect(clean_scss, sender=apps.get_model('dbsettings', 'Setting'))
