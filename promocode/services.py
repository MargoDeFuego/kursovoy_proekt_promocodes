"""Business services for promo-code lifecycle operations."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from .models import Promo, PromoClick

User = get_user_model()


def deactivate_expired_promos() -> int:
    """Deactivate all active promo codes whose expiration date is in the past."""
    return Promo.objects.filter(expires_at__lt=timezone.localdate(), is_active=True).update(is_active=False)


def get_client_ip(request: HttpRequest) -> str | None:
    """Return client IP address from request headers."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def register_promo_click(promo: Promo, request: HttpRequest) -> PromoClick:
    """Create analytic click row and increment usage counter when promo is revealed."""
    user = request.user if request.user.is_authenticated else None
    click = PromoClick.objects.create(
        promo=promo,
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )
    Promo.objects.filter(pk=promo.pk).update(used_count=models_increment("used_count"))
    return click


def models_increment(field_name: str) -> Any:
    """Return database expression for atomic increment."""
    from django.db.models import F

    return F(field_name) + 1


def visible_promos_for_user(user: Any) -> QuerySet[Promo]:
    """Return promo queryset according to role rules."""
    qs = Promo.objects.select_related("shop", "created_by").prefetch_related("groups")
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return qs
    return qs.filter(is_active=True)
