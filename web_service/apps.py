import os

from django.apps import AppConfig

from whatsapp.main import start


class WebServiceConfig(AppConfig):
    name = 'web_service'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            start()
