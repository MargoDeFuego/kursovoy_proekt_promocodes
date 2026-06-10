"""Бизнес‑логика для операций жизненного цикла промокодов."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from .models import Promo, PromoClick
from .auth_utils import get_site_user

User = get_user_model()


def deactivate_expired_promos() -> int:
    """Деактивировать все активные промокоды с истёкшим сроком действия."""
    return Promo.objects.filter(expires_at__lt=timezone.localdate(), is_active=True).update(is_active=False)


def get_client_ip(request: HttpRequest) -> str | None:
    """Вернуть IP‑адрес клиента из заголовков запроса."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def register_promo_click(promo: Promo, request: HttpRequest) -> PromoClick:
    """Создать запись клика и атомарно увеличить счётчик использований."""
    site_user = get_site_user(request)
    user = site_user or (request.user if request.user.is_authenticated else None)
    click = PromoClick.objects.create(
        promo=promo,
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )
    Promo.objects.filter(pk=promo.pk).update(used_count=models_increment("used_count"))
    return click


def models_increment(field_name: str) -> Any:
    """Вернуть выражение F() для атомарного инкремента поля."""
    from django.db.models import F

    return F(field_name) + 1


def visible_promos_for_user(user: Any) -> QuerySet[Promo]:
    """Вернуть queryset промокодов согласно правилам ролей."""
    qs = Promo.objects.select_related("shop", "created_by").prefetch_related("groups")
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return qs
    return qs.filter(is_active=True)
