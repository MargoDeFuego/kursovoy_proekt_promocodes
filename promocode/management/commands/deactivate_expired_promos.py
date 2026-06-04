"""Management command to deactivate expired promo codes."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from promocode.services import deactivate_expired_promos


class Command(BaseCommand):
    """Deactivate expired promo codes."""

    help = "Деактивирует истёкшие промокоды"

    def handle(self, *args: object, **options: object) -> None:
        """Run deactivation and print result."""
        count = deactivate_expired_promos()
        self.stdout.write(self.style.SUCCESS(f"Деактивировано промокодов: {count}"))
