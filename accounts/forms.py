import phonenumbers
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UsernameField,
)
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from phonenumbers.phonenumberutil import NumberParseException


class UserRegisterForm(UserCreationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        "class": "input",
        "placeholder": "ism_familiya",
        "type": "text",
        "autocomplete": "off",
        "name": "custom-username-field",  # Уникальное значение для имени поля
        "id": "custom-username-field",  # Уникальное значение для идентификатора поля
    }))

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Проверяем, что имя пользователя не содержит пробелов
        if ' ' in username:
            raise forms.ValidationError('Имя пользователя не может содержать пробелы.')

        # Проверяем уникальность имени пользователя
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Это имя пользователя уже занято.')

        return username

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
            "placeholder": "телефон номер или @имя пользователя",
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
        validators=[MinLengthValidator(limit_value=8, message="Пароль должен содержать минимум 8 символов.")],
    )

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')

        try:
            parsed_telephone = phonenumbers.parse(telephone, None)
            if phonenumbers.is_valid_number(parsed_telephone):
                formatted_telephone = phonenumbers.format_number(parsed_telephone, phonenumbers.PhoneNumberFormat.E164)
                return formatted_telephone
        except NumberParseException:
            pass

        raise ValidationError(_('Пожалуйста, введите правильный номер телефона.'))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Этот email уже используется."))

        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise ValidationError(_("Пароли не совпадают. Пожалуйста, введите одинаковые пароли."))

        return cleaned_data

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
