from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Promo
from .serializers import PromoSerializer


class PromoViewSet(ModelViewSet):
    """
    REST API для промокодов
    """
    serializer_class = PromoSerializer
    queryset = Promo.objects.select_related("shop")
    search_fields = ("title", "code")

    # ✔ использование Q
    def get_queryset(self):
        return Promo.objects.filter(
            Q(is_active=True) | Q(expires_at__isnull=True)
        )

    # ✔ @action(detail=False)
    @action(methods=["GET"], detail=False)
    def active(self, request):
        promos = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(promos, many=True)
        return Response(serializer.data)

    # ✔ @action(detail=True)
    @action(methods=["POST"], detail=True)
    def deactivate(self, request, pk=None):
        promo = self.get_object()
        promo.is_active = False
        promo.save()
        return Response({"status": "promo deactivated"})
