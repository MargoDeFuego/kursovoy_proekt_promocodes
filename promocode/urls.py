from django.urls import path
from . import views

urlpatterns = [
    path("", views.group_list, name="group_list"),
    path("groups/<slug:slug>/", views.group_detail, name="group_detail"),

    path("promos/", views.promo_list, name="promo_list"),
    path("promo/add/", views.promo_create, name="promo_create"),
    path("promo/<int:pk>/", views.promo_detail, name="promo_detail"),
    path("promo/<int:pk>/edit/", views.promo_update, name="promo_update"),
    path("promo/<int:pk>/delete/", views.promo_delete, name="promo_delete"),
]

# --- DRF router (подключаем только если DRF установлен) ---
from rest_framework.routers import DefaultRouter
from .api_views import PromoViewSet

router = DefaultRouter()
router.register(r"api/promos", PromoViewSet, basename="promo")

urlpatterns += router.urls
