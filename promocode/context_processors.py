"""Контекстные процессоры для публичной части сайта промокодов."""

from __future__ import annotations

from django.http import HttpRequest

from .auth_utils import get_public_user


def site_auth(request: HttpRequest) -> dict[str, object]:
    """Передать в шаблоны пользователя публичного сайта отдельно от Django admin ``request.user``."""
    site_user = get_public_user(request)
    return {
        "site_user": site_user,
        "site_user_is_authenticated": site_user is not None,
    }
