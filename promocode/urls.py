from django.urls import path
from . import views

urlpatterns = [
    # главная — группы
    path("", views.group_list, name="group_list"),

    # группа → промокоды
    path("groups/<slug:slug>/", views.group_detail, name="group_detail"),

    # CRUD промокодов
    path("create/", views.promo_create, name="promo_create"),
    path("<int:pk>/", views.promo_detail, name="promo_detail"),
    path("<int:pk>/edit/", views.promo_update, name="promo_update"),
    path("<int:pk>/delete/", views.promo_delete, name="promo_delete"),
]
