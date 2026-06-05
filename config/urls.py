"""Project URL configuration."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),

    # Logout — разрешаем GET и POST, чтобы исключить 405
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="promo_list",
            http_method_names=["get", "post"]
        ),
        name="logout",
    ),

    # Login (без logout!)
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),

    # Select2
    path("select2/", include("django_select2.urls")),

    # Social auth
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
