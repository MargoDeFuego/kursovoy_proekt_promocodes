from django import forms
from .models import Promo


class PromoForm(forms.ModelForm):
    class Meta:
        model = Promo
        fields = [
            "shop",
            "title",
            "code",
            "description",
            "is_active",
            "expires_at",
            "groups",  
        ]
        widgets = {
            "groups": forms.CheckboxSelectMultiple(),
        }
