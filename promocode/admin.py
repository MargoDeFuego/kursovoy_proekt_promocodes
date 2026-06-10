"""Конфигурация админ‑панели для каталога промокодов."""

from __future__ import annotations

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin

from .models import Promo, PromoClick, PromoGroup, Shop


class PromoResource(resources.ModelResource):
    """Ресурс импорта/экспорта промокодов с оптимизированным queryset и кастомными полями."""

    shop_name = fields.Field(column_name="shop_name")
    groups_list = fields.Field(column_name="groups")

    class Meta:
        model = Promo
        fields = (
            "id",
            "title",
            "code",
            "description",
            "discount_percent",
            "min_order_amount",
            "usage_limit",
            "used_count",
            "is_active",
            "created_at",
            "expires_at",
            "shop_name",
            "groups_list",
        )

    def get_export_queryset(self, request):
        """Экспортировать только активные промокоды с оптимизированными связями."""
        return Promo.objects.select_related("shop").prefetch_related("groups").filter(is_active=True)

    def dehydrate_code(self, obj: Promo) -> str:
        """Маскировать промокод при экспорте."""
        return (obj.code[:4] + "****") if obj.code else "—"

    def dehydrate_shop_name(self, obj: Promo) -> str:
        """Экспортировать название магазина."""
        return obj.shop.name if obj.shop_id else "—"

    def dehydrate_groups_list(self, obj: Promo) -> str:
        """Экспортировать список групп через запятую."""
        return ", ".join(group.name for group in obj.groups.all())


class PromoInline(admin.TabularInline):
    """Встроенный список промокодов на странице магазина."""

    model = Promo
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("title", "code", "discount_percent", "is_active", "expires_at", "created_at")


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Админ‑панель магазинов с аннотацией количества промокодов."""

    list_display = ("name", "category", "website", "promo_count")
    list_display_links = ("name",)
    search_fields = ("name", "category")
    inlines = (PromoInline,)

    def get_queryset(self, request):
        """Аннотировать количество промокодов для отображения в списке."""
        return super().get_queryset(request).annotate(_promo_count=Count("promos"))

    @admin.display(description="Кол-во промокодов", ordering="_promo_count")
    def promo_count(self, obj: Shop) -> int:
        """Вернуть аннотированное количество промокодов."""
        return obj._promo_count


@admin.register(Promo)
class PromoAdmin(ImportExportModelAdmin):
    """Админ‑панель промокодов с группами, ссылками на магазины и бизнес‑полями."""

    resource_class = PromoResource
    list_display = (
        "title",
        "shop_link",
        "discount_percent",
        "min_order_amount",
        "used_count",
        "usage_limit",
        "is_active",
        "expires_at",
        "groups_links",
        "hidden_code",
        "click_count",
    )
    list_display_links = ("title",)
    list_filter = ("shop", "is_active", "created_at", "expires_at", "groups", "discount_percent")
    search_fields = ("title", "code", "shop__name", "groups__name")
    date_hierarchy = "created_at"
    raw_id_fields = ("shop", "created_by")
    readonly_fields = ("created_at",)
    filter_horizontal = ("groups",)

    fieldsets = (
        ("Основное", {"fields": ("shop", "title", "description", "created_by")}),
        ("Промокод и активность", {"fields": ("code", "is_active", "expires_at", "groups")}),
        ("Бизнес-условия", {"fields": ("discount_percent", "min_order_amount", "usage_limit", "used_count")}),
        ("Служебное", {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        """Optimize admin query and annotate click count."""
        return (
            super()
            .get_queryset(request)
            .select_related("shop", "created_by")
            .prefetch_related("groups")
            .annotate(_click_count=Count("clicks", distinct=True))
        )

    @admin.display(description="Промокод")
    def hidden_code(self, obj: Promo) -> str:
        """Показать полный промокод в админке."""
        return obj.code or "—"

    @admin.display(description="Магазин")
    def shop_link(self, obj: Promo) -> str:
        """Вернуть ссылку на магазин в админке."""
        if not obj.shop_id:
            return "—"
        url = reverse("admin:promocode_shop_change", args=[obj.shop_id])
        return format_html('<a href="{}">{}</a>', url, obj.shop.name)

    @admin.display(description="Группы")
    def groups_links(self, obj: Promo) -> str:
        """Вернуть ссылки на группы в админке."""
        groups = obj.groups.all()
        if not groups:
            return "—"
        links = []
        for group in groups:
            url = reverse("admin:promocode_promogroup_change", args=[group.id])
            links.append(format_html('<a href="{}">{}</a>', url, group.name))
        return format_html(", ".join(str(link) for link in links))

    @admin.display(description="Клики", ordering="_click_count")
    def click_count(self, obj: Promo) -> int:
        """Вернуть аннотированное количество кликов."""
        return obj._click_count


@admin.register(PromoGroup)
class PromoGroupAdmin(admin.ModelAdmin):
    """Админ‑панель групп промокодов."""

    list_display = ("name", "slug", "promo_count")
    list_display_links = ("name",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        """Аннотировать количество промокодов в группе."""
        return super().get_queryset(request).annotate(_promo_count=Count("promos", distinct=True))

    @admin.display(description="Кол-во промокодов", ordering="_promo_count")
    def promo_count(self, obj: PromoGroup) -> int:
        """Вернуть аннотированное количество промокодов."""
        return obj._promo_count


@admin.register(PromoClick)
class PromoClickAdmin(admin.ModelAdmin):
    """Админ‑панель аналитики кликов (только для чтения)."""

    list_display = ("promo", "user", "ip_address", "created_at")
    list_filter = ("created_at",)
    search_fields = ("promo__title", "promo__code", "user__username", "ip_address")
    readonly_fields = ("promo", "user", "ip_address", "user_agent", "created_at")

    def has_add_permission(self, request) -> bool:
        """Запретить ручное добавление кликов."""
        return False
