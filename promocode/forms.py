"""Формы для управления промокодами на сайте."""

from django import forms
from django.core.validators import MinLengthValidator
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import Promo


class PromoForm(forms.ModelForm):
    """Форма промокода с явной валидацией и виджетами Select2."""

    title = forms.CharField(
        min_length=5,
        error_messages={
            "min_length": "Название должно содержать минимум 5 символов.",
            "required": "Введите название промокода.",
        },
    )

    code = forms.CharField(
        min_length=5,
        error_messages={
            "min_length": "Код должен содержать минимум 5 символов.",
            "required": "Введите код промокода.",
        },
    )

    class Meta:
        model = Promo
        fields = [
            "shop",
            "title",
            "code",
            "description",
            "discount_percent",
            "min_order_amount",
            "usage_limit",
            "used_count",
            "is_active",
            "expires_at",
            "groups",
        ]
        widgets = {
            "shop": Select2Widget(attrs={"data-placeholder": "Выберите магазин"}),
            "groups": Select2MultipleWidget(attrs={"data-placeholder": "Выберите группы"}),
            "expires_at": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        """Запустить встроенную валидацию и вернуть очищенные данные."""
        
        cleaned_data = super().clean()
        return cleaned_data
