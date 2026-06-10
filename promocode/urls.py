"""URL‑маршруты для приложения промокодов и его API."""

from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import PromoGroupViewSet, PromoViewSet, ShopViewSet

urlpatterns = [
    # Регистрация
    path("register/", views.register, name="register"),

    # Группы
    path("", views.group_list, name="group_list"),
    path("groups/<slug:slug>/", views.group_detail, name="group_detail"),

    # Магазины
    path("shops/", views.shop_list, name="shop_list"),
    path("shops/<int:pk>/", views.shop_detail, name="shop_detail"),
    path("shops/add/", views.shop_create, name="shop_create"),
    path("shops/<int:pk>/edit/", views.shop_update, name="shop_update"),
    path("shops/<int:pk>/delete/", views.shop_delete, name="shop_delete"),



    # Промокоды
    path("promos/", views.promo_list, name="promo_list"),
    path("promo/add/", views.promo_create, name="promo_create"),
    path("promo/<int:pk>/", views.promo_detail, name="promo_detail"),
    path("promo/<int:pk>/reveal/", views.promo_reveal, name="promo_reveal"),
    path("promo/<int:pk>/reveal-list/", views.promo_reveal_list, name="promo_reveal_list"),
    path("promo/<int:pk>/edit/", views.promo_update, name="promo_update"),
    path("promo/<int:pk>/delete/", views.promo_delete, name="promo_delete"),

    
]

# API
router = DefaultRouter()
router.register(r"api/promos", PromoViewSet, basename="promo")
router.register(r"api/shops", ShopViewSet, basename="shop")
router.register(r"api/groups", PromoGroupViewSet, basename="promo-group")
urlpatterns += router.urls
