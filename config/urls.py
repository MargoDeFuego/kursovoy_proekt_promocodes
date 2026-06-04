"""Project URL configuration."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Select2
    path("select2/", include("django_select2.urls")),

    # Django built‑in auth (login, logout, password reset)
    # Это исправляет ошибку /accounts/login/
    path("accounts/", include("django.contrib.auth.urls")),

    # Social auth (Google OAuth)
    path("auth/", include("social_django.urls", namespace="social")),

    # Основное приложение
    path("", include("promocode.urls")),
]

# Debug-only routes
if settings.DEBUG:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
