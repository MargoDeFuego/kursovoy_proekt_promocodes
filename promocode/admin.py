from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Shop, Promo, PromoGroup


class PromoInline(admin.TabularInline):
    model = Promo
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "promo_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = (PromoInline,)

    @admin.display(description="Кол-во промокодов")
    def promo_count(self, obj):
        return obj.promos.count()


@admin.register(Promo)
class PromoAdmin(ImportExportModelAdmin):
    list_display = (
        "title",
        "shop",
        "is_active",
        "created_at",
        "expires_at",
        "hidden_code",
    )
    list_display_links = ("title",)
    list_filter = ("shop", "is_active", "created_at", "expires_at", "groups")
    search_fields = ("title", "code", "shop__name")
    date_hierarchy = "created_at"

    raw_id_fields = ("shop",)
    readonly_fields = ("created_at",)
    filter_horizontal = ("groups",)

    @admin.display(description="Промокод")
    def hidden_code(self, obj):
        return obj.code or "—"


@admin.register(PromoGroup)
class PromoGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "promo_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Кол-во промокодов")
    def promo_count(self, obj):
        return obj.promos.count()
