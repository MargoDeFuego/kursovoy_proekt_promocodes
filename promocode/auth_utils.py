"""Separate front-site authentication helpers.

The Django admin uses the standard Django auth session (``request.user``).
The public promo-code site uses a separate session key so that logging out
from the personal account does not destroy the administrator session.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

SITE_USER_SESSION_KEY = "site_user_id"
F = TypeVar("F", bound=Callable[..., HttpResponse])


def get_site_user(request: HttpRequest) -> Any | None:
    """Return user stored in the public-site session or ``None``.

    Invalid/stale user ids are removed from the session automatically.
    """
    user_id = request.session.get(SITE_USER_SESSION_KEY)
    if not user_id:
        return None

    User = get_user_model()
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        request.session.pop(SITE_USER_SESSION_KEY, None)
        request.session.modified = True
        return None


def set_site_user(request: HttpRequest, user: Any) -> None:
    """Store public-site user without changing Django admin authentication."""
    request.session[SITE_USER_SESSION_KEY] = user.pk
    request.session.modified = True


def clear_site_user(request: HttpRequest) -> None:
    """Log out only from the public-site account."""
    request.session.pop(SITE_USER_SESSION_KEY, None)
    request.session.modified = True


def site_user_is_authenticated(request: HttpRequest) -> bool:
    """Return ``True`` when a public-site user is logged in."""
    return get_site_user(request) is not None


def site_login_required(view_func: F) -> F:
    """Require either public-site login or standard Django admin login.

    Staff users authenticated in Django admin should still be able to reveal
    promo codes without using a separate public-site account.
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if get_site_user(request) is not None:
            return view_func(request, *args, **kwargs)
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect(f"/accounts/login/?next={request.path}")

    return cast(F, wrapper)
