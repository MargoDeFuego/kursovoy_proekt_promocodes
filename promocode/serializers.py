from rest_framework import serializers
from .models import Promo, Shop


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = "__all__"
        extra_kwargs = {
            "code": {"required": False},
        }

    #кастомная валидация
    def validate_code(self, value):
        if value and len(value) < 5:
            raise serializers.ValidationError(
                "Промокод должен быть не короче 5 символов"
            )
        return value


#  2-я модель для API 
class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"
