from django import forms
from .models import Promo

class PromoForm(forms.ModelForm):
    class Meta:
        model = Promo
        fields = ["shop", "title", "code", "description", "expires_at", "is_active"]
