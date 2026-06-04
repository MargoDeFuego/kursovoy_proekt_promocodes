"""Tests for promo-code business logic and API."""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from .models import Promo, PromoGroup, Shop
from .services import deactivate_expired_promos

User = get_user_model()


class PromoBusinessLogicTests(TestCase):
    """Business validation tests."""

    def setUp(self) -> None:
        """Create base shop for tests."""
        self.shop = Shop.objects.create(name="Test Shop", website="https://example.com")

    def test_shop_website_must_start_with_http(self) -> None:
        """Invalid shop website must raise validation error."""
        shop = Shop(name="Bad", website="example.com")
        with self.assertRaises(ValidationError):
            shop.full_clean()

    def test_code_is_uppercased_on_save(self) -> None:
        """Promo code should be normalized to uppercase."""
        promo = Promo.objects.create(shop=self.shop, title="Sale", code="abcde", discount_percent=10)
        self.assertEqual(promo.code, "ABCDE")

    def test_short_code_is_masked(self) -> None:
        """List representation should hide code."""
        promo = Promo.objects.create(shop=self.shop, title="Sale", code="ABCDE", discount_percent=10)
        self.assertEqual(promo.short_code(), "•••••")

    def test_discount_must_be_in_range(self) -> None:
        """Discount cannot be over 100%."""
        promo = Promo(shop=self.shop, title="Bad", code="ABCDE", discount_percent=101)
        with self.assertRaises(ValidationError):
            promo.full_clean()

    def test_active_promo_cannot_be_expired(self) -> None:
        """Active promo cannot have expiration date in the past."""
        promo = Promo(
            shop=self.shop,
            title="Expired",
            code="EXPIRED",
            discount_percent=10,
            expires_at=timezone.localdate() - timedelta(days=1),
            is_active=True,
        )
        with self.assertRaises(ValidationError):
            promo.full_clean()

    def test_usage_limit_detection(self) -> None:
        """Promo must detect reached usage limit."""
        promo = Promo.objects.create(
            shop=self.shop,
            title="Limit",
            code="LIMIT1",
            discount_percent=10,
            usage_limit=1,
            used_count=1,
        )
        self.assertTrue(promo.is_usage_limit_reached)

    def test_duplicate_active_code_for_same_shop_is_forbidden(self) -> None:
        """Only one active promo with the same code per shop is allowed."""
        Promo.objects.create(shop=self.shop, title="First", code="DUPLI", discount_percent=10)
        duplicate = Promo(shop=self.shop, title="Second", code="DUPLI", discount_percent=20)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_deactivate_expired_promos_service(self) -> None:
        """Service must deactivate expired promos."""
        promo = Promo.objects.create(shop=self.shop, title="Old", code="OLDDD", discount_percent=10, is_active=False)
        Promo.objects.filter(pk=promo.pk).update(is_active=True, expires_at=timezone.localdate() - timedelta(days=2))
        count = deactivate_expired_promos()
        promo.refresh_from_db()
        self.assertEqual(count, 1)
        self.assertFalse(promo.is_active)


class PromoApiTests(APITestCase):
    """API tests for serializers, filters and role permissions."""

    def setUp(self) -> None:
        """Create fixtures for API tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.admin = User.objects.create_user(username="admin", password="pass12345", is_staff=True)
        self.shop = Shop.objects.create(name="Electro Shop", website="https://shop.example", category="electronics")
        self.group = PromoGroup.objects.create(name="Electronics", slug="electronics")
        self.promo = Promo.objects.create(shop=self.shop, title="Phone sale", code="PHONE10", discount_percent=10)
        self.promo.groups.add(self.group)

    def test_api_list_hides_code_for_guest(self) -> None:
        """Guest should see masked public code."""
        response = self.client.get("/api/promos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["public_code"], "•••••")

    def test_api_reveal_requires_authentication(self) -> None:
        """Reveal action must require authenticated user."""
        response = self.client.get(f"/api/promos/{self.promo.pk}/reveal/")
        self.assertEqual(response.status_code, 403)

    def test_api_reveal_returns_code_for_buyer(self) -> None:
        """Authenticated buyer may reveal available promo code."""
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/api/promos/{self.promo.pk}/reveal/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["public_code"], "PHONE10")

    def test_filter_by_discount_min(self) -> None:
        """API should filter promos by minimum discount."""
        response = self.client.get("/api/promos/?discount_min=5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_staff_can_create_promo(self) -> None:
        """Staff user may create promo through API."""
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/promos/",
            {
                "shop": self.shop.pk,
                "title": "New sale",
                "code": "NEW10",
                "discount_percent": 10,
                "groups": [self.group.pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
