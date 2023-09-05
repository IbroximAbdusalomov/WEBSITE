from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    password_validation,
    UsernameField,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model


class UserRegisterForm(UserCreationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        "class": "input",
        "placeholder": "имя пользователя",
        "type": "text",
        "autocomplete": "off",
        "name": "custom-username-field",  # Уникальное значение для имени поля
        "id": "custom-username-field",  # Уникальное значение для идентификатора поля
    }))

    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            "class": "input",
            "type": "email",
            "placeholder": "user@gmail.com",
            "autocomplete": "email",
        })
    )

    telephone = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "номер телеграмма",
        })
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=True,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "class": "input",
            "placeholder": "Пароль",
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "class": "input",
            "placeholder": "Повторите пароль",
        }),
        strip=True,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            # "first_name",
            # "last_name",
            "email",
            "telephone"
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": "input"}),
            # "first_name": forms.TextInput(attrs={"class": "form-control"}),
            # "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "input"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        "autofocus": True,
        "class": "input",
        "placeholder": "Имя пользователя",
    }))

    password = forms.CharField(
        label=_("Password"),
        strip=True,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": "password",
            "placeholder": "Пароль",
            "type": "password",
        }),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email"
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
