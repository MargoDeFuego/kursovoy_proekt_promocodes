"""Создаёт демонстрационные магазины, группы и промокоды для локальной разработки."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from promocode.models import Promo, PromoGroup, Shop


class Command(BaseCommand):
    """Заполняет базу данных демонстрационными данными для страниц промокодов."""

    help = "Создаёт демонстрационные магазины, группы и промокоды. Можно запускать многократно."

    def handle(self, *args: object, **options: object) -> None:
        """Создаёт или обновляет демонстрационные записи."""
        User = get_user_model()
        admin = User.objects.filter(is_staff=True).first()

        electronics, _ = PromoGroup.objects.get_or_create(
            slug="electronics",
            defaults={"name": "Электроника"},
        )
        clothes, _ = PromoGroup.objects.get_or_create(
            slug="clothes",
            defaults={"name": "Одежда"},
        )
        marketplaces, _ = PromoGroup.objects.get_or_create(
            slug="marketplaces",
            defaults={"name": "Маркетплейсы"},
        )

        tech_shop, _ = Shop.objects.get_or_create(
            name="Tech Store",
            defaults={
                "website": "https://example.com/tech",
                "category": "electronics",
            },
        )
        fashion_shop, _ = Shop.objects.get_or_create(
            name="Fashion Market",
            defaults={
                "website": "https://example.com/fashion",
                "category": "clothes",
            },
        )
        market_shop, _ = Shop.objects.get_or_create(
            name="Big Marketplace",
            defaults={
                "website": "https://example.com/market",
                "category": "marketplace",
            },
        )

        expires_at = timezone.localdate() + timedelta(days=30)
        demos = [
            {
                "shop": tech_shop,
                "title": "Скидка на электронику 15%",
                "code": "TECH15",
                "description": "Демо-промокод для проверки списка, деталей и API.",
                "discount_percent": 15,
                "min_order_amount": Decimal("1000.00"),
                "usage_limit": 100,
                "groups": [electronics, marketplaces],
            },
            {
                "shop": fashion_shop,
                "title": "Одежда со скидкой 20%",
                "code": "STYLE20",
                "description": "Активный промокод для витрины магазина одежды.",
                "discount_percent": 20,
                "min_order_amount": Decimal("1500.00"),
                "usage_limit": 50,
                "groups": [clothes],
            },
            {
                "shop": market_shop,
                "title": "Маркетплейс: бесплатная доставка",
                "code": "SHIPFREE",
                "description": "Промокод для проверки группы маркетплейсов.",
                "discount_percent": 5,
                "min_order_amount": Decimal("500.00"),
                "usage_limit": None,
                "groups": [marketplaces],
            },
        ]

        created_or_updated = 0
        for demo in demos:
            groups = demo.pop("groups")
            promo, _ = Promo.objects.update_or_create(
                shop=demo["shop"],
                code=demo["code"],
                defaults={
                    **demo,
                    "is_active": True,
                    "expires_at": expires_at,
                    "created_by": admin,
                },
            )
            promo.groups.set(groups)
            created_or_updated += 1

        self.stdout.write(self.style.SUCCESS(f"Демонстрационные данные готовы: {created_or_updated} промокодов."))
