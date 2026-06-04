"""URL routes for promo-code application and API."""

from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import PromoGroupViewSet, PromoViewSet, ShopViewSet

urlpatterns = [
    path("", views.group_list, name="group_list"),
    path("groups/<slug:slug>/", views.group_detail, name="group_detail"),
    path("promos/", views.promo_list, name="promo_list"),
    path("promo/add/", views.promo_create, name="promo_create"),
    path("promo/<int:pk>/", views.promo_detail, name="promo_detail"),
    path("promo/<int:pk>/reveal/", views.promo_reveal, name="promo_reveal"),
    path("promo/<int:pk>/edit/", views.promo_update, name="promo_update"),
    path("promo/<int:pk>/delete/", views.promo_delete, name="promo_delete"),
]

router = DefaultRouter()
router.register(r"api/promos", PromoViewSet, basename="promo")
router.register(r"api/shops", ShopViewSet, basename="shop")
router.register(r"api/groups", PromoGroupViewSet, basename="promo-group")
urlpatterns += router.urls
