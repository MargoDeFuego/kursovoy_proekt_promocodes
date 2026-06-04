"""DRF serializers for promo-code API."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .models import Promo, PromoGroup, Shop


class ShopSerializer(serializers.ModelSerializer):
    """Serializer for shops."""

    promo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Shop
        fields = ("id", "name", "logo", "website", "category", "promo_count")


class PromoGroupSerializer(serializers.ModelSerializer):
    """Serializer for promo groups/categories."""

    promo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PromoGroup
        fields = ("id", "name", "slug", "promo_count")


class PromoSerializer(serializers.ModelSerializer):
    """Serializer with context-based code visibility and computed fields."""

    shop_name = serializers.SerializerMethodField()
    group_names = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    discount_label = serializers.SerializerMethodField()
    public_code = serializers.SerializerMethodField()
    click_count = serializers.IntegerField(read_only=True, default=0)
    code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Promo
        fields = (
            "id",
            "shop",
            "shop_name",
            "title",
            "code",
            "public_code",
            "description",
            "discount_percent",
            "discount_label",
            "min_order_amount",
            "usage_limit",
            "used_count",
            "is_active",
            "status",
            "created_at",
            "expires_at",
            "groups",
            "group_names",
            "created_by",
            "click_count",
        )
        read_only_fields = ("created_by", "created_at", "used_count")

    def get_shop_name(self, obj: Promo) -> str:
        """Return related shop name without extra queries if select_related is used."""
        return obj.shop.name

    def get_group_names(self, obj: Promo) -> list[str]:
        """Return group/category names."""
        return [group.name for group in obj.groups.all()]

    def get_status(self, obj: Promo) -> str:
        """Return user-friendly promo status."""
        if not obj.is_active:
            return "inactive"
        if obj.is_expired:
            return "expired"
        if obj.is_usage_limit_reached:
            return "usage_limit_reached"
        return "active"

    def get_discount_label(self, obj: Promo) -> str:
        """Return text label for discount."""
        return f"Скидка {obj.discount_percent}%"

    def get_public_code(self, obj: Promo) -> str:
        """Return hidden or visible code depending on serializer context."""
        if self.context.get("reveal_codes"):
            return obj.code
        request = self.context.get("request")
        if request and getattr(request.user, "is_staff", False):
            return obj.code
        return "•••••"

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate business rules through model.clean().

        Many-to-many fields cannot be assigned directly to a Django model instance
        before it is saved. DRF will save them later through serializer.save(),
        so here we skip them and validate only scalar/model fields.
        """
        instance = self.instance or Promo()
        many_to_many_fields = {"groups"}

        for key, value in attrs.items():
            if key in many_to_many_fields:
                continue
            setattr(instance, key, value)

        if not instance.expires_at and "expires_at" not in attrs and self.instance:
            instance.expires_at = self.instance.expires_at

        try:
            instance.clean()
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise serializers.ValidationError(exc.message_dict) from exc
            raise serializers.ValidationError(exc.messages) from exc

        return attrs

    def validate_expires_at(self, value: Any) -> Any:
        """Reject past expiration dates for new active promo codes."""
        if value and value < timezone.localdate():
            raise serializers.ValidationError("Дата окончания не может быть в прошлом.")
        return value
