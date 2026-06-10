"""Конфигурация приложения 'promocode'."""

from django.apps import AppConfig

class PromocodeConfig(AppConfig):
    """AppConfig для приложения промокодов."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "promocode"
    verbose_name = "Промокоды"
