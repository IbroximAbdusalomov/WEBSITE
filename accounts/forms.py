import phonenumbers
from django import forms
from films.models import Categories, SubCategories, Tag
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import (
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from phonenumbers.phonenumberutil import NumberParseException


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "telephone"
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": "input"}),
            "email": forms.EmailInput(attrs={"class": "input"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
        }

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

    email = forms.EmailField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "email",
        "placeholder": "user@gmail.com",
        "autocomplete": "email",
    }))

    telephone = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "placeholder": "телефон номер или @имя пользователя",
    }))

    password1 = forms.CharField(label=_("Password"), strip=True, widget=forms.PasswordInput(attrs={
        "autocomplete": "new-password",
        "class": "input",
        "placeholder": "Пароль", }),
                                validators=[MinLengthValidator(limit_value=8,
                                                               message="Пароль должен содержать минимум 8 символов.")], )

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
        error_messages={
            'required': _('Поле "Пароль" обязательно для заполнения.'),
            'invalid': _('Неверный формат пароля.'),
        },
    )


class CompanyForm1(forms.Form):
    name = forms.CharField(
        label='Название компании',
        widget=forms.TextInput(attrs={'class': 'company-input'})
    )
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        empty_label='Выберите категорию',
        required=True,
        label='Категория',
        widget=forms.Select(attrs={'class': 'company-select', 'id': 'id_category'})
    )
    sub_category = forms.ChoiceField(
        # choices=[('', 'Выберите подкатегорию')] + [],
        required=True,
        label='Подкатегория',
        widget=forms.Select(attrs={'class': 'company-select', 'id': 'id_sub_category'})
    )

    tags = forms.ModelMultipleChoiceField(
        label='',
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_tags'}),
    )


class CompanyForm2(forms.Form):
    telegram = forms.CharField(max_length=100, required=True, label='Telegram',
                               widget=forms.TextInput(attrs={'class': 'company-input'})
                               )
    whatsapp = forms.CharField(max_length=100, required=True, label='WhatsApp',
                               widget=forms.TextInput(attrs={'class': 'company-input'})
                               )
    website = forms.CharField(max_length=100, required=True, label='Website',
                              widget=forms.TextInput(attrs={'class': 'company-input'})
                              )
    url_maps = forms.CharField(max_length=200, required=True, label='Выведите урл Яндекс карты или Гугл карты',
                               widget=forms.TextInput(attrs={'class': 'company-input url-maps-class'})
                               )


class CompanyForm3(forms.Form):
    logo = forms.ImageField(required=True, label='Добавить логотип',
                            widget=forms.FileInput(attrs={'class': 'company-input', 'id': 'file-input__logo'}))
    banner = forms.ImageField(required=True, label='Баннер',
                              widget=forms.FileInput(attrs={'class': 'company-input', 'id': 'file-input__banner'}))


class CompanyForm4(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'company-input'}), required=True,
                                  label='Описание компании')
    country = forms.CharField(max_length=100, required=True, label='Страна',
                              widget=forms.TextInput(attrs={'class': 'company-input'}))
