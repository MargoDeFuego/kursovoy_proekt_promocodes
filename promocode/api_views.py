from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils.timezone import now

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Promo, Shop
from .serializers import PromoSerializer, ShopSerializer


class PromoViewSet(ModelViewSet):
    """
    REST API для промокодов
    """
    serializer_class = PromoSerializer
    queryset = Promo.objects.select_related("shop")
    search_fields = ("title", "code")

    # фильтрация (варианты) + поиск + сортировка
    filter_backends = [DjangoFilterBackend, SearchFilter]
    # 1) filter по именованному аргументу: /api/promos/by-group/<id>/
    # 2) filter по GET параметрам: ?shop=1
    # 3) filter по GET параметрам: ?is_active=true
    # 4) filter по диапазону дат: ?expires_at__gte=2026-01-01&expires_at__lte=2026-12-31
    # 5) SearchFilter: ?search=слово
    filterset_fields = {
        "shop": ["exact"],
        "is_active": ["exact"],
        "groups": ["exact"],
        "expires_at": ["gte", "lte"],
    }
    ordering_fields = ("created_at", "expires_at")

    # 2 осмысленных Q-запроса с OR + AND + NOT (|, &, ~)
    def get_queryset(self):
        today = now().date()

        # Q №1: активные И (не просрочены) ИЛИ без даты окончания
        q_active_and_valid = (Q(is_active=True) & (Q(expires_at__gte=today) | Q(expires_at__isnull=True)))

        # Q №2: НЕ (пустой/короткий код) — пример NOT
        q_not_bad_code = ~Q(code__isnull=True) & ~Q(code="")

        return (
            Promo.objects
            .select_related("shop")
            .filter(q_active_and_valid & q_not_bad_code)
        )

    # @action(detail=False)
    @action(methods=["GET"], detail=False)
    def active(self, request):
        promos = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(promos, many=True)
        return Response(serializer.data)

    # @action(detail=True)
    @action(methods=["POST"], detail=True)
    def deactivate(self, request, pk=None):
        promo = self.get_object()
        promo.is_active = False
        promo.save()
        return Response({"status": "promo deactivated"})

    # фильтр по именованному аргументу в url (вариант фильтрации)
    @action(methods=["GET"], detail=False, url_path=r"by-group/(?P<group_id>\d+)")
    def by_group(self, request, group_id=None):
        promos = self.get_queryset().filter(groups__id=group_id)
        page = self.paginate_queryset(promos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(promos, many=True)
        return Response(serializer.data)


# API для 2-й модели (Shop) — нужно для "минимум 2 модели"
class ShopViewSet(ModelViewSet):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ("name",)
