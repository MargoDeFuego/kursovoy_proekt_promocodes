from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

"""Форма регистрации пользователя с обязательным полем email."""

class RegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя."""
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
