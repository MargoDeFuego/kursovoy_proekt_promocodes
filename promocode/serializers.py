from rest_framework import serializers
from .models import Promo


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = "__all__"
        extra_kwargs = {
            "code": {"required": False},
        }

    # ✔ кастомная валидация (по требованиям)
    def validate_code(self, value):
        if value and len(value) < 5:
            raise serializers.ValidationError(
                "Промокод должен быть не короче 5 символов"
            )
        return value
