"""Команда управления для деактивации просроченных промокодов."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from promocode.services import deactivate_expired_promos


class Command(BaseCommand):
    """Деактивирует просроченные промокоды."""

    help = "Деактивирует истёкшие промокоды"

    def handle(self, *args: object, **options: object) -> None:
        """Запускает деактивацию и выводит результат."""
        
        count = deactivate_expired_promos()
        self.stdout.write(self.style.SUCCESS(f"Деактивировано промокодов: {count}"))
