"""Модели приложения каталога промокодов."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Shop(models.Model):
    """Магазин, для которого публикуются промокоды."""

    name = models.CharField("Название магазина", max_length=100)
    logo = models.ImageField("Логотип магазина", upload_to="shops/", blank=True, null=True)
    website = models.URLField("Сайт магазина", blank=True)
    category = models.CharField(
        "Категория магазина",
        max_length=100,
        blank=True,
        help_text="Например: электроника, одежда, продукты, маркетплейс.",
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
        ordering = ("name",)

    def __str__(self) -> str:
        """Вернуть название магазина."""
        return self.name

    def clean(self) -> None:
        """Проверить бизнес-правила магазина."""
        super().clean()
        if self.website and not self.website.startswith(("http://", "https://")):
            raise ValidationError({"website": "Сайт должен начинаться с http:// или https://"})


class PromoGroup(models.Model):
    """Группа/категория промокодов."""

    name = models.CharField("Название группы", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True)

    class Meta:
        verbose_name = "Группа промокодов"
        verbose_name_plural = "Группы промокодов"
        ordering = ("name",)

    def __str__(self) -> str:
        """Вернуть название группы."""
        return self.name


class Promo(models.Model):
    """Промокод магазина с бизнес-валидацией срока, скидки и лимита применений."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="promos",
        verbose_name="Магазин",
    )
    title = models.CharField("Название акции", max_length=255)
    code = models.CharField("Промокод", max_length=50)
    description = models.TextField("Описание акции", blank=True)
    discount_percent = models.PositiveSmallIntegerField(
        "Скидка, %",
        default=10,
        help_text="Значение от 1 до 100.",
    )
    min_order_amount = models.DecimalField(
        "Минимальная сумма заказа",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    usage_limit = models.PositiveIntegerField(
        "Лимит применений",
        blank=True,
        null=True,
        help_text="Оставьте пустым, если лимита нет.",
    )
    used_count = models.PositiveIntegerField("Использовано", default=0)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    expires_at = models.DateField("Дата окончания", blank=True, null=True)
    groups = models.ManyToManyField(
        PromoGroup,
        related_name="promos",
        verbose_name="Группы",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_promos",
        verbose_name="Кто создал",
        blank=True,
        null=True,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("shop", "code"),
                condition=Q(is_active=True),
                name="unique_active_promo_code_per_shop",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть понятное строковое представление промокода."""
        return f"{self.shop} — {self.title}"

    @property
    def is_expired(self) -> bool:
        """Проверить, истёк ли срок действия промокода."""
        return bool(self.expires_at and self.expires_at < timezone.localdate())

    @property
    def is_usage_limit_reached(self) -> bool:
        """Проверить, достигнут ли лимит применений промокода."""
        return self.usage_limit is not None and self.used_count >= self.usage_limit

    def can_be_used(self) -> bool:
        """Вернуть True, если промокод активен, не истёк и не исчерпал лимит."""
        return self.is_active and not self.is_expired and not self.is_usage_limit_reached

    def short_code(self) -> str:
        """Скрытое отображение кода для списков."""
        return "•••••"

    short_code.short_description = "Промокод"

    def clean(self) -> None:
        """Проверить бизнес-правила промокода."""
        super().clean()
        errors: dict[str, str] = {}

        if self.code:
            normalized_code = self.code.strip().upper()
            if len(normalized_code) < 5:
                errors["code"] = "Промокод должен быть не короче 5 символов."
            if not all(ch.isalnum() or ch in "-_" for ch in normalized_code):
                errors["code"] = "Промокод может содержать только буквы, цифры, дефис и подчёркивание."

        if not 1 <= self.discount_percent <= 100:
            errors["discount_percent"] = "Скидка должна быть от 1 до 100%."

        if self.min_order_amount < 0:
            errors["min_order_amount"] = "Минимальная сумма заказа не может быть отрицательной."

        if self.usage_limit is not None and self.used_count > self.usage_limit:
            errors["used_count"] = "Использований не может быть больше лимита."

        if self.is_active and self.expires_at and self.expires_at < timezone.localdate():
            errors["expires_at"] = "Активный промокод не может иметь прошедшую дату окончания."

        if self.shop_id and self.code:
            duplicate_qs = Promo.objects.filter(
                shop_id=self.shop_id,
                code=self.code.strip().upper(),
                is_active=True,
            )
            if self.pk:
                duplicate_qs = duplicate_qs.exclude(pk=self.pk)
            if self.is_active and duplicate_qs.exists():
                errors["code"] = "У этого магазина уже есть активный промокод с таким кодом."

        if errors:
            raise ValidationError(errors)

    def save(self, *args: object, **kwargs: object) -> None:
        """Нормализовать код и выполнить полную валидацию перед сохранением."""
        if self.code:
            self.code = self.code.strip().upper()
        self.full_clean()
        super().save(*args, **kwargs)


class PromoClick(models.Model):
    """Факт раскрытия/клика по промокоду для аналитики и аннотаций."""

    promo = models.ForeignKey(
        Promo,
        on_delete=models.CASCADE,
        related_name="clicks",
        verbose_name="Промокод",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="promo_clicks",
        verbose_name="Пользователь",
    )
    ip_address = models.GenericIPAddressField("IP-адрес", blank=True, null=True)
    user_agent = models.TextField("User Agent", blank=True)
    created_at = models.DateTimeField("Дата клика", auto_now_add=True)

    class Meta:
        verbose_name = "Клик по промокоду"
        verbose_name_plural = "Клики по промокодам"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Вернуть подпись клика."""
        return f"{self.promo_id} — {self.created_at:%Y-%m-%d %H:%M}"
