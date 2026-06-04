from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Select2 
    path("select2/", include("django_select2.urls")),

    # маршруты приложения
    path('', include('promocode.urls')),
]

# Медиа-файлы в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
