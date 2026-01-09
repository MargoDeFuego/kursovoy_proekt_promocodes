from django.shortcuts import render, get_object_or_404, redirect
from .models import Promo, PromoGroup
from .forms import PromoForm


# ─────────────────────────────
# Part 3 tutorial — LIST / READ
# ─────────────────────────────

def group_list(request):
    """
    Главная страница — список групп
    """
    groups = PromoGroup.objects.all()
    return render(
        request,
        "promocode/group_list.html",
        {"groups": groups}
    )


def group_detail(request, slug):
    """
    Страница одной группы — список промокодов группы
    """
    group = get_object_or_404(PromoGroup, slug=slug)
    promos = group.promos.select_related("shop").order_by("-created_at")

    return render(
        request,
        "promocode/group_detail.html",
        {
            "group": group,
            "promos": promos,
        }
    )


def promo_list(request):
    """
    Список всех промокодов (пример READ LIST)
    """
    promos = Promo.objects.select_related("shop").order_by("-created_at")
    return render(
        request,
        "promocode/promo_list.html",
        {"promos": promos}
    )


def promo_detail(request, pk):
    """
    Детальный просмотр промокода (READ ONE)
    """
    promo = get_object_or_404(Promo, pk=pk)
    return render(
        request,
        "promocode/promo_detail.html",
        {"promo": promo}
    )


# ─────────────────────────────
# Part 4 tutorial — FORMS / POST
# ─────────────────────────────

def promo_create(request):
    """
    Добавление промокода (CREATE)
    """
    form = PromoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("promo_list")

    return render(
        request,
        "promocode/promo_form.html",
        {"form": form}
    )


def promo_update(request, pk):
    """
    Редактирование промокода (UPDATE)
    """
    promo = get_object_or_404(Promo, pk=pk)
    form = PromoForm(request.POST or None, instance=promo)

    if form.is_valid():
        form.save()
        return redirect("promo_detail", pk=pk)

    return render(
        request,
        "promocode/promo_form.html",
        {"form": form}
    )


def promo_delete(request, pk):
    """
    Удаление промокода (DELETE)
    """
    promo = get_object_or_404(Promo, pk=pk)

    if request.method == "POST":
        promo.delete()
        return redirect("promo_list")

    return render(
        request,
        "promocode/promo_confirm_delete.html",
        {"promo": promo}
    )
