"""HTML‑представления для каталога промокодов."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, logout as django_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .filters import PromoFilter
from .forms import PromoForm
from .forms_auth import RegisterForm
from .models import Promo, PromoGroup, Shop
from .services import register_promo_click
from .auth_utils import clear_site_user, get_public_user, set_site_user, site_login_required


def staff_required(function):
    """Разрешить доступ только сотрудникам (is_staff)."""
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff)(function)


# -----------------------------
#   АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ САЙТА
# -----------------------------
def site_login(request: HttpRequest) -> HttpResponse:
    """Войти на публичный сайт, не затрагивая сессию Django‑админки."""
    next_url = request.GET.get("next") or request.POST.get("next") or "promo_list"

    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            set_site_user(request, form.get_user())
            return redirect(next_url)
    else:
        form = AuthenticationForm(request=request)

    return render(request, "registration/login.html", {"form": form, "next": next_url})


def site_logout(request: HttpRequest) -> HttpResponse:
    """Выйти из публичного аккаунта, не разлогинивая администратора."""
    should_logout_django_user = request.user.is_authenticated and not request.user.is_staff

    clear_site_user(request)
    if should_logout_django_user:
        django_logout(request)

    messages.success(request, "Вы вышли из личного кабинета.")
    return redirect("promo_list")


# -----------------------------
#   РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
# -----------------------------
def register(request: HttpRequest) -> HttpResponse:
    """Зарегистрировать нового пользователя и авторизовать его только на публичном сайте."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get("password1")
            authenticated_user = authenticate(
                request,
                username=user.username,
                password=raw_password,
            )
            if authenticated_user is not None:
                set_site_user(request, authenticated_user)
            return redirect("promo_list")
    else:
        form = RegisterForm()

    return render(request, "promocode/register.html", {"form": form})


# -----------------------------
#   ПРОМОКОДЫ / ГРУППЫ / МАГАЗИНЫ
# -----------------------------

def group_list(request: HttpRequest) -> HttpResponse:
    """Показать список групп промокодов с количеством активных акций."""
    groups = PromoGroup.objects.annotate(
        promo_count=Count("promos", filter=Q(promos__is_active=True))
    ).order_by("name")
    return render(request, "promocode/group_list.html", {"groups": groups})


def shop_list(request: HttpRequest) -> HttpResponse:
    """Показать магазины с количеством активных промокодов и статистикой кликов."""
    today = now().date()
    shops = (
        Shop.objects.annotate(
            active_promo_count=Count(
                "promos",
                filter=Q(promos__is_active=True)
                & (Q(promos__expires_at__gte=today) | Q(promos__expires_at__isnull=True)),
                distinct=True,
            ),
            total_promo_count=Count("promos", distinct=True),
            total_click_count=Count("promos__clicks", distinct=True),
        )
        .order_by("name")
    )
    return render(request, "promocode/shop_list.html", {"shops": shops})


def group_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Показать промокоды выбранной группы."""
    group = get_object_or_404(PromoGroup, slug=slug)
    today = now().date()
    promo_qs = (
        group.promos.select_related("shop", "created_by")
        .prefetch_related("groups")
        .annotate(click_count=Count("clicks", distinct=True))
        .filter(is_active=True)
        .filter(Q(expires_at__gte=today) | Q(expires_at__isnull=True))
        .order_by("-created_at")
    )
    paginator = Paginator(promo_qs, 3)
    promos = paginator.get_page(request.GET.get("page"))
    return render(request, "promocode/group_detail.html", {"group": group, "promos": promos})


def promo_list(request: HttpRequest) -> HttpResponse:
    """Показать активные промокоды с поиском, фильтрами и пагинацией."""
    search_query = request.GET.get("q", "").strip()
    today = now().date()
    promo_qs = (
        Promo.objects.select_related("shop", "created_by")
        .prefetch_related("groups")
        .annotate(click_count=Count("clicks", distinct=True))
        .filter(is_active=True)
        .filter(Q(expires_at__gte=today) | Q(expires_at__isnull=True))
        .order_by("-created_at")
    )

    promo_filter = PromoFilter(request.GET or None, queryset=promo_qs)
    promo_qs = promo_filter.qs

    if search_query:
        promo_qs = promo_qs.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(shop__name__icontains=search_query)
        )

    query_params = request.GET.copy()
    query_params.pop("page", None)
    paginator = Paginator(promo_qs, 5)
    promos = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "promocode/promo_list.html",
        {
            "filter": promo_filter,
            "filter_querystring": query_params.urlencode(),
            "promos": promos,
            "q": search_query,
        },
    )


def promo_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Показать подробности промокода."""
    promo = get_object_or_404(
        Promo.objects.select_related("shop", "created_by")
        .prefetch_related("groups")
        .annotate(click_count=Count("clicks")),
        pk=pk,
    )
    return render(request, "promocode/promo_detail.html", {"promo": promo})


@site_login_required
def promo_reveal(request: HttpRequest, pk: int) -> HttpResponse:
    """Раскрыть промокод и зарегистрировать клик."""
    promo = get_object_or_404(Promo.objects.select_related("shop"), pk=pk)
    if promo.can_be_used():
        register_promo_click(promo, request)
    return render(request, "promocode/promo_detail.html", {"promo": promo, "reveal_code": True})


@require_POST
def promo_reveal_list(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX‑раскрытие промокода со страницы списка.""" 
    # Блокируем гостей, но разрешаем оба варианта входа:
    # обычный вход сайта через site_user_id и Google OAuth через request.user.
    if get_public_user(request) is None and not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse(
            {"ok": False, "error": "Авторизуйтесь, чтобы увидеть промокод."},
            status=403,
        )

    promo = get_object_or_404(Promo.objects.select_related("shop"), pk=pk)

    if not promo.can_be_used():
        return JsonResponse(
            {"ok": False, "error": "Промокод недоступен или срок его действия истёк."},
            status=400,
        )

    register_promo_click(promo, request)
    """AJAX POST на promo_reveal_list"""
    return JsonResponse(
        {
            "ok": True,
            "code": promo.code,
            "click_count": promo.clicks.count(),
        }
    )



@staff_required
def promo_create(request: HttpRequest) -> HttpResponse:
    """Создать новый промокод (только для сотрудников)."""
    form = PromoForm(request.POST or None)
    if form.is_valid():
        promo = form.save(commit=False)
        promo.created_by = request.user
        promo.save()
        form.save_m2m()
        return redirect("promo_list")
    return render(request, "promocode/promo_form.html", {"form": form})


@staff_required
def promo_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактировать промокод."""
    promo = get_object_or_404(Promo, pk=pk)
    form = PromoForm(request.POST or None, instance=promo)
    if form.is_valid():
        form.save()
        return redirect("promo_detail", pk=pk)
    return render(request, "promocode/promo_form.html", {"form": form})


@staff_required
def promo_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Удалить промокод."""
    promo = get_object_or_404(Promo, pk=pk)
    if request.method == "POST":
        promo.delete()
        return redirect("promo_list")
    return render(request, "promocode/promo_confirm_delete.html", {"promo": promo})

def shop_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Показать информацию о магазине и его активные промокоды."""
    today = now().date()
    shop = get_object_or_404(
        Shop.objects.annotate(
            active_promo_count=Count(
                "promos",
                filter=Q(promos__is_active=True)
                & (Q(promos__expires_at__gte=today) | Q(promos__expires_at__isnull=True)),
                distinct=True,
            ),
            total_promo_count=Count("promos", distinct=True),
            total_click_count=Count("promos__clicks", distinct=True),
        ),
        pk=pk,
    )
    promos = (
        Promo.objects.select_related("shop", "created_by")
        .prefetch_related("groups")
        .annotate(click_count=Count("clicks", distinct=True))
        .filter(shop=shop, is_active=True)
        .filter(Q(expires_at__gte=today) | Q(expires_at__isnull=True))
        .order_by("-created_at")
    )
    return render(request, "promocode/shop_detail.html", {"shop": shop, "promos": promos})


@staff_required
def shop_create(request):
    """Создать магазин."""
    form = ShopForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("shop_list")
    return render(request, "promocode/shop_form.html", {"form": form})

@staff_required
def shop_update(request, pk):
    """Редактировать магазин."""
    shop = get_object_or_404(Shop, pk=pk)
    form = ShopForm(request.POST or None, instance=shop)
    if form.is_valid():
        form.save()
        return redirect("shop_detail", pk=pk)
    return render(request, "promocode/shop_form.html", {"form": form})

@staff_required
def shop_delete(request, pk):
    """Удалить магазин."""
    shop = get_object_or_404(Shop, pk=pk)
    if request.method == "POST":
        shop.delete()
        return redirect("shop_list")
    return render(request, "promocode/shop_confirm_delete.html", {"shop": shop})
