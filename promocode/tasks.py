"""Celery tasks for promo-code project."""

from __future__ import annotations

from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone

from .models import Promo
from .services import deactivate_expired_promos


@shared_task
def deactivate_expired_promos_task() -> int:
    """Celery task: deactivate expired active promo codes."""
    count = deactivate_expired_promos()
    send_expiring_promos_report.delay("test@example.com")
    return count


@shared_task
def send_expiring_promos_report(email: str) -> int:
    """Send report about promo codes expiring within 7 days via Mailhog/SMPP backend."""
    today = timezone.localdate()
    limit = today + timezone.timedelta(days=7)
    promos = (
        Promo.objects.select_related("shop")
        .annotate(click_count=Count("clicks"))
        .filter(is_active=True, expires_at__range=(today, limit))
        .order_by("expires_at")
    )
    lines = [f"{promo.shop.name}: {promo.title} до {promo.expires_at}" for promo in promos]
    body = "\n".join(lines) or "Промокодов, истекающих в ближайшие 7 дней, нет."
    send_mail("Отчёт по истекающим промокодам", body, None, [email], fail_silently=False)
    return promos.count()
