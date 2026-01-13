from django.core.management.base import BaseCommand
from django.utils.timezone import now
from promocode.models import Promo


class Command(BaseCommand):
    help = "Деактивирует истёкшие промокоды"

    def handle(self, *args, **options):
        count = Promo.objects.filter(
            expires_at__lt=now().date(),
            is_active=True
        ).update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(f"Деактивировано промокодов: {count}")
        )
