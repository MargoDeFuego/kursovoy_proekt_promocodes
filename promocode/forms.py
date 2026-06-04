"""Forms for promo-code management pages."""

from __future__ import annotations

from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import Promo


class PromoForm(forms.ModelForm):
    """Form with model-level business validation for promo codes."""

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

    def clean(self) -> dict[str, object]:
        """Run Django Model.clean() through ModelForm validation."""
        cleaned_data = super().clean()
        return cleaned_data
