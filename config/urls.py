"""Project URL configuration."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from promocode import views as promocode_views

urlpatterns = [
    # Logout for the public site only: does not flush Django admin session.
    path("logout/", promocode_views.site_logout, name="logout"),

    # Login for the public site only: stores user in a separate session key.
    path("accounts/login/", promocode_views.site_login, name="login"),

    # Main app.
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
