"""Project URL configuration."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. Твой logout — САМЫЙ ПЕРВЫЙ
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="promo_list",
            http_method_names=["get", "post"]
        ),
        name="logout",
    ),

    # 2. Login
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),

    # 3. Основное приложение — ВАЖНО: ставим ПЕРЕД social-auth
    path("", include("promocode.urls")),

    # 4. Social auth — ниже, чтобы не перехватывал logout
    path("auth/", include("social_django.urls", namespace="social")),

    # 5. Select2
    path("select2/", include("django_select2.urls")),

    # 6. Админка — всегда внизу
    path("admin/", admin.site.urls),
]


# Debug-only routes
if settings.DEBUG:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
