"""Django Filter classes for the promo API."""

from __future__ import annotations

import django_filters
from django import forms
from django.db.models import QuerySet

from .models import Promo, PromoGroup, Shop


class PromoFilter(django_filters.FilterSet):
    """Filter promos by shop, category/group, discount, date and min order amount."""

    shop = django_filters.ModelChoiceFilter(
        queryset=Shop.objects.all(),
        field_name="shop",
        label="Магазин",
        empty_label="Все магазины",
    )
    manufacturer = django_filters.CharFilter(
        field_name="shop__name",
        lookup_expr="icontains",
        label="Производитель / магазин",
    )
    shop_name = django_filters.CharFilter(
        field_name="shop__name",
        lookup_expr="icontains",
        label="Название магазина",
    )
    category = django_filters.ModelChoiceFilter(
        queryset=PromoGroup.objects.all(),
        method="filter_category",
        label="Категория",
        empty_label="Все категории",
    )
    group = django_filters.ModelChoiceFilter(
        queryset=PromoGroup.objects.all(),
        method="filter_category",
        label="Группа",
        empty_label="Все группы",
    )
    discount_min = django_filters.NumberFilter(
        field_name="discount_percent",
        lookup_expr="gte",
        label="Скидка от, %",
    )
    discount_max = django_filters.NumberFilter(
        field_name="discount_percent",
        lookup_expr="lte",
        label="Скидка до, %",
    )
    price_min = django_filters.NumberFilter(
        field_name="min_order_amount",
        lookup_expr="gte",
        label="Минимальный заказ от",
    )
    price_max = django_filters.NumberFilter(
        field_name="min_order_amount",
        lookup_expr="lte",
        label="Минимальный заказ до",
    )
    expires_from = django_filters.DateFilter(
        field_name="expires_at",
        lookup_expr="gte",
        label="Действует после",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    expires_to = django_filters.DateFilter(
        field_name="expires_at",
        lookup_expr="lte",
        label="Действует до",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    is_active = django_filters.BooleanFilter(field_name="is_active", label="Активен")

    class Meta:
        model = Promo
        fields = (
            "shop",
            "manufacturer",
            "shop_name",
            "category",
            "group",
            "discount_min",
            "discount_max",
            "price_min",
            "price_max",
            "expires_from",
            "expires_to",
            "is_active",
        )

    def filter_category(self, queryset: QuerySet[Promo], name: str, value: PromoGroup) -> QuerySet[Promo]:
        """Filter promo codes by selected PromoGroup."""
        if not value:
            return queryset
        return queryset.filter(groups=value).distinct()
