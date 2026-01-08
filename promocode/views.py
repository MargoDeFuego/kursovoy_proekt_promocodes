from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Promo, PromoGroup
from .forms import PromoForm


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
    Страница одной группы — промокоды этой группы
    """
    group = get_object_or_404(PromoGroup, slug=slug)

    promos = (
        group.promos
        .filter(is_active=True)
        .select_related("shop")
        .order_by("-created_at")
    )

    return render(
        request,
        "promocode/group_detail.html",
        {
            "group": group,
            "promos": promos,
        }
    )


# ─── ниже твой CRUD, не трогаем ───

def promo_detail(request, pk):
    promo = get_object_or_404(Promo, pk=pk)
    return render(request, "promocode/promo_detail.html", {"promo": promo})


def promo_create(request):
    form = PromoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("group_list")
    return render(request, "promocode/promo_form.html", {"form": form})


def promo_update(request, pk):
    promo = get_object_or_404(Promo, pk=pk)
    form = PromoForm(request.POST or None, instance=promo)
    if form.is_valid():
        form.save()
        return redirect("promo_detail", pk=pk)
    return render(request, "promocode/promo_form.html", {"form": form})


def promo_delete(request, pk):
    promo = get_object_or_404(Promo, pk=pk)
    if request.method == "POST":
        promo.delete()
        return redirect("group_list")
    return render(
        request,
        "promocode/promo_confirm_delete.html",
        {"promo": promo}
    )
