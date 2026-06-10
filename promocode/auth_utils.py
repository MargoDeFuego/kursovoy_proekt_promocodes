"""Вспомогательные функции авторизации для публичного сайта.

Админ‑панель Django использует стандартную сессию аутентификации (``request.user``).
Публичная часть сайта промокодов использует отдельный ключ сессии, чтобы выход
из личного кабинета не разлогинивал администратора.
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
    """Вернуть пользователя, сохранённого в сессии публичного сайта, или ``None``.

    Некорректные или устаревшие ID пользователей автоматически удаляются из сессии.
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
    """Сохранить пользователя публичного сайта, не затрагивая админ‑сессию Django."""
    request.session[SITE_USER_SESSION_KEY] = user.pk
    request.session.modified = True


def clear_site_user(request: HttpRequest) -> None:
    """Выйти только из аккаунта публичного сайта."""
    request.session.pop(SITE_USER_SESSION_KEY, None)
    request.session.modified = True


def get_public_user(request: HttpRequest) -> Any | None:
    """Вернуть пользователя публичного сайта.

    Публичная часть может аутентифицировать пользователей двумя способами:
    * обычная форма логина сохраняет ``site_user_id`` в сессии;
    * Google OAuth использует стандартный ``request.user``.

    Сотрудники/админы намеренно НЕ считаются пользователями публичного сайта,
    чтобы их админ‑сессия не смешивалась с пользовательской.
    """
    site_user = get_site_user(request)
    if site_user is not None:
        return site_user

    request_user = getattr(request, "user", None)
    if (
        request_user is not None
        and request_user.is_authenticated
        and not request_user.is_staff
    ):
        return request_user

    return None


def site_user_is_authenticated(request: HttpRequest) -> bool:
    """Вернуть ``True``, если пользователь публичного сайта авторизован."""
    return get_public_user(request) is not None


def site_login_required(view_func: F) -> F:
    """Требовать авторизацию публичного сайта или вход в Django‑админку.

    Администраторы, вошедшие в админ‑панель, также могут открывать промокоды
    без отдельного логина на публичном сайте.
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if get_public_user(request) is not None:
            return view_func(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect(f"/accounts/login/?next={request.path}")

    return cast(F, wrapper)
