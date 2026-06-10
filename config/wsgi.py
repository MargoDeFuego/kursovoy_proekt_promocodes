"""
WSGI‑конфигурация для проекта config.

Этот файл предоставляет WSGI‑приложение как переменную уровня модуля
с именем ``application``.

Подробную информацию об этом файле можно найти по ссылке:
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
