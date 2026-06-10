"""API‑представления для каталога промокодов."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q
from django.utils.timezone import now
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .filters import PromoFilter
from .models import Promo, PromoGroup, Shop
from .serializers import PromoGroupSerializer, PromoSerializer, ShopSerializer
from .services import register_promo_click, visible_promos_for_user


class PromoRolePermission(permissions.BasePermission):
     """Права доступа: админы управляют всем, авторизованные пользователи могут открывать/кликать, гости — только читать активные промокоды."""

    def has_permission(self, request: Request, view: Any) -> bool:
        """Проверить права доступа для текущего действия."""
        if view.action in {"list", "retrieve", "active", "by_group"}:
            return True
        if view.action in {"reveal", "click"}:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class PromoViewSet(ModelViewSet):
    """REST API для промокодов с оптимизированным queryset, аннотациями и фильтрами."""

    serializer_class = PromoSerializer
    permission_classes = (PromoRolePermission,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = PromoFilter
    search_fields = ("title", "code", "description", "shop__name", "groups__name")
    ordering_fields = ("created_at", "expires_at", "discount_percent", "min_order_amount", "click_count")
    ordering = ("-created_at",)

    def get_queryset(self):
        """Вернуть оптимизированный queryset с select_related, prefetch_related и аннотацией кликов."""
        today = now().date()
        q_active_and_valid = Q(is_active=True) & (Q(expires_at__gte=today) | Q(expires_at__isnull=True))
        q_has_code = ~Q(code__isnull=True) & ~Q(code="")

        base_qs = visible_promos_for_user(self.request.user)
        if not (self.request.user and self.request.user.is_staff):
            base_qs = base_qs.filter(q_active_and_valid & q_has_code)

        return (
            base_qs.select_related("shop", "created_by")
            .prefetch_related("groups")
            .annotate(click_count=Count("clicks", distinct=True))
        )

    def get_serializer_context(self) -> dict[str, Any]:
        """Передать в сериализатор роль пользователя и флаг видимости промокода."""
        context = super().get_serializer_context()
        context["role"] = "admin" if self.request.user.is_staff else "buyer"
        context["reveal_codes"] = self.action in {"reveal"}
        return context

    def perform_create(self, serializer: PromoSerializer) -> None:
        """Установить текущего пользователя как создателя промокода."""
        serializer.save(created_by=self.request.user)

    @action(methods=["GET"], detail=False)
    def active(self, request: Request) -> Response:
        """Вернуть список активных и валидных промокодов."""
        promos = self.get_queryset().filter(is_active=True)
        page = self.paginate_queryset(promos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(promos, many=True).data)

    @action(methods=["POST"], detail=True)
    def deactivate(self, request: Request, pk: int | None = None) -> Response:
        """Деактивировать промокод (доступно только сотрудникам)."""
        promo = self.get_object()
        promo.is_active = False
        promo.save(update_fields=("is_active",))
        return Response({"status": "promo deactivated"})

    @action(methods=["GET"], detail=True)
    def reveal(self, request: Request, pk: int | None = None) -> Response:
         """Показать промокод авторизованному пользователю и зарегистрировать клик."""
        promo = self.get_object()
        if not promo.can_be_used():
            return Response({"detail": "Промокод недоступен."}, status=status.HTTP_400_BAD_REQUEST)
        register_promo_click(promo, request)
        serializer = self.get_serializer(promo)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True)
    def click(self, request: Request, pk: int | None = None) -> Response:
        """Зарегистрировать клик без раскрытия промокода."""
        promo = self.get_object()
        register_promo_click(promo, request)
        return Response({"status": "click registered"})

    @action(methods=["GET"], detail=False, url_path=r"by-group/(?P<group_id>\d+)")
    def by_group(self, request: Request, group_id: int | None = None) -> Response:
        """Отфильтровать промокоды по ID группы из URL."""
        promos = self.get_queryset().filter(groups__id=group_id).distinct()
        page = self.paginate_queryset(promos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(promos, many=True).data)


class ShopViewSet(ModelViewSet):
    """API для магазинов с аннотацией количества промокодов."""

    serializer_class = ShopSerializer
    queryset = Shop.objects.annotate(promo_count=Count("promos")).order_by("name")
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "category")
    ordering_fields = ("name", "promo_count")


class PromoGroupViewSet(ReadOnlyModelViewSet):
     """Read‑only API для категорий/групп промокодов."""

    serializer_class = PromoGroupSerializer
    queryset = PromoGroup.objects.annotate(promo_count=Count("promos")).order_by("name")
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "slug")
    ordering_fields = ("name", "promo_count")
