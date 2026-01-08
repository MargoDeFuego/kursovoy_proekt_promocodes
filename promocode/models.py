from django.db import models


class Shop(models.Model):
    name = models.CharField(
        "Название магазина",
        max_length=100
    )
    logo = models.ImageField(
        "Логотип магазина",
        upload_to="shops/",
        blank=True,
        null=True
    )
    website = models.URLField(
        "Сайт магазина",
        blank=True
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return self.name

class PromoGroup(models.Model):
    name = models.CharField(
        "Название группы",
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        "Slug",
        max_length=120,
        unique=True
    )

    class Meta:
        verbose_name = "Группа промокодов"
        verbose_name_plural = "Группы промокодов"
        ordering = ("name",)

    def __str__(self):
        return self.name
        
class Promo(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="promos",
        verbose_name="Магазин"
    )
    title = models.CharField(
        "Название акции",
        max_length=255
    )
    code = models.CharField(
        "Промокод",
        max_length=50
    )
    description = models.TextField(
        "Описание акции",
        blank=True
    )
    is_active = models.BooleanField(
        "Активен",
        default=True
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True
    )
    expires_at = models.DateField(
        "Дата окончания",
        blank=True,
        null=True
    )
    groups = models.ManyToManyField(
        PromoGroup,
        related_name="promos",
        verbose_name="Группы",
        blank=True
    )

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.shop} — {self.title}"

    def short_code(self):
        return "•••••"
    short_code.short_description = "Промокод"


