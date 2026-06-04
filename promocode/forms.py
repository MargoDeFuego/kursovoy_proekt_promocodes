from django import forms
from .models import Promo
from django_select2.forms import Select2Widget, Select2MultipleWidget

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
            "shop": Select2Widget,               # Select2
            "groups": Select2MultipleWidget,     
        }
