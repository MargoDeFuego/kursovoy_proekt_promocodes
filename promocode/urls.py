from django.urls import path
from . import views

urlpatterns = [
    # Главная — список групп
    path("", views.group_list, name="group_list"),

    # Группа → промокоды группы
    path("groups/<slug:slug>/", views.group_detail, name="group_detail"),

    # CRUD промокодов (tutorial Part 3–4)
    path("promos/", views.promo_list, name="promo_list"),                 # READ LIST
    path("promo/add/", views.promo_create, name="promo_create"),          # CREATE
    path("promo/<int:pk>/", views.promo_detail, name="promo_detail"),     # READ ONE
    path("promo/<int:pk>/edit/", views.promo_update, name="promo_update"),# UPDATE
    path("promo/<int:pk>/delete/", views.promo_delete, name="promo_delete"),# DELETE
]
