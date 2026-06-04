"""Django Filter classes for the promo API."""

from __future__ import annotations

import django_filters
from django.db.models import QuerySet

from .models import Promo


class PromoFilter(django_filters.FilterSet):
    """Filter promos by shop, category/group, discount, date and min order amount."""

    shop = django_filters.NumberFilter(field_name="shop_id")
    manufacturer = django_filters.CharFilter(field_name="shop__name", lookup_expr="icontains")
    shop_name = django_filters.CharFilter(field_name="shop__name", lookup_expr="icontains")
    category = django_filters.NumberFilter(method="filter_category")
    group = django_filters.NumberFilter(method="filter_category")
    discount_min = django_filters.NumberFilter(field_name="discount_percent", lookup_expr="gte")
    discount_max = django_filters.NumberFilter(field_name="discount_percent", lookup_expr="lte")
    price_min = django_filters.NumberFilter(field_name="min_order_amount", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="min_order_amount", lookup_expr="lte")
    expires_from = django_filters.DateFilter(field_name="expires_at", lookup_expr="gte")
    expires_to = django_filters.DateFilter(field_name="expires_at", lookup_expr="lte")
    is_active = django_filters.BooleanFilter(field_name="is_active")

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

    def filter_category(self, queryset: QuerySet[Promo], name: str, value: int) -> QuerySet[Promo]:
        """Filter promo codes by PromoGroup id."""
        return queryset.filter(groups__id=value).distinct()
