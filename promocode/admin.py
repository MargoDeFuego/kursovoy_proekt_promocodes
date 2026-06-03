from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

from .models import Shop, Promo, PromoGroup


# ресурс для экспорта + 3 кастомизации
class PromoResource(resources.ModelResource):
    shop_name = fields.Field(column_name="shop_name")
    groups_list = fields.Field(column_name="groups")

    class Meta:
        model = Promo
        fields = ("id", "title", "code", "description", "is_active", "created_at", "expires_at", "shop_name", "groups_list")

    # 1) кастомизация get_export_queryset
    def get_export_queryset(self, request):
        return Promo.objects.select_related("shop").prefetch_related("groups").filter(is_active=True)

    # 2) кастомизация dehydrate_{field_name}
    def dehydrate_code(self, obj):
        # маскируем часть кода, чтобы показать кастомизацию экспорта
        return (obj.code[:4] + "****") if obj.code else "—"

    # 3) кастомизация get_{field_name}
    def dehydrate_shop_name(self, obj):
        return obj.shop.name if obj.shop_id else "—"
    def dehydrate_groups_list(self, obj):
        return ", ".join(g.name for g in obj.groups.all())


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
    resource_class = PromoResource  

    list_display = (
        "title",
        "shop_link",          
        "is_active",
        "created_at",
        "expires_at",
        "groups_links",     
        "hidden_code",
    )
    list_display_links = ("title",)
    list_filter = ("shop", "is_active", "created_at", "expires_at", "groups")
    search_fields = ("title", "code", "shop__name")
    date_hierarchy = "created_at"

    raw_id_fields = ("shop",)
    readonly_fields = ("created_at",)
    filter_horizontal = ("groups",)

    # fields / fieldsets
    fieldsets = (
        ("Основное", {
            "fields": ("shop", "title", "description")
        }),
        ("Промокод и активность", {
            "fields": ("code", "is_active", "expires_at", "groups")
        }),
        ("Служебное", {
            "fields": ("created_at",)
        }),
    )

    @admin.display(description="Промокод")
    def hidden_code(self, obj):
        return obj.code or "—"

    # гиперссылка на связанный Shop
    @admin.display(description="Магазин")
    def shop_link(self, obj):
        if not obj.shop_id:
            return "—"
        url = reverse("admin:promocode_shop_change", args=[obj.shop_id])
        return format_html('<a href="{}">{}</a>', url, obj.shop.name)

    # гиперссылки на связанные группы
    @admin.display(description="Группы")
    def groups_links(self, obj):
        groups = obj.groups.all()
        if not groups:
            return "—"
        links = []
        for g in groups:
            url = reverse("admin:promocode_promogroup_change", args=[g.id])
            links.append(format_html('<a href="{}">{}</a>', url, g.name))
        return format_html(", ".join(str(l) for l in links))


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
