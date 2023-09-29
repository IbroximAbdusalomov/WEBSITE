import re
import phonenumbers
from django import forms
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from phonenumbers.phonenumberutil import NumberParseException
from .models import Films, City, Country, Categories, SubCategories, Tag


class FilmsForm(forms.ModelForm):
    class Meta:
        model = Films
        fields = ['title', 'description', 'category', 'sub_category', 'tags', 'telephone', 'telegram', 'country',
                  'city', 'image']

    title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-input'}), max_length=100, )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': _('Введите описание'), 'rows': '4'}),
        max_length=800,
    )

    category = forms.ModelChoiceField(
        label='',
        queryset=Categories.objects.all(),
        empty_label="Выберите категорию",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_category", "name": "category", }),
    )

    sub_category = forms.ModelChoiceField(
        label='',
        queryset=SubCategories.objects.all(),
        empty_label="Выберите субкатегорию",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_sub_category", "name": "sub_category", }),
    )

    tags = forms.ModelMultipleChoiceField(
        label='',
        queryset=Tag.objects.all(),  # Замените на ваш запрос для выбора тегов
        widget=forms.CheckboxSelectMultiple,  # Используем виджет для выбора нескольких значений
    )

    telephone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('+998 66 666 66 66')}),
        validators=[RegexValidator(
            regex=r'^\+\d{3}(\d{2} \d{3} \d{2} \d{2}|\d{2}\d{3}\d{2}\d{2})$',  # Добавляем два формата номера
            message=_('Введите номер телефона в формате: "+998 66 666 66 66" или "+998666666666"'),
        )]
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

    telegram = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-input', 'placeholder': _('+998 66 666 66 66 или @имя пользователя')}
        ),
        error_messages={
            'required': _('Это поле обязательно для заполнения.'),
            'invalid': _('Пожалуйста, введите правильный номер телефона или имя пользователя в Telegram.')
        }
    )

    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram')

        try:
            parsed_telegram = phonenumbers.parse(telegram, None)
            if phonenumbers.is_valid_number(parsed_telegram):
                return telegram
        except NumberParseException:
            pass

        # Проверяем, является ли введенное значение именем пользователя в Telegram (начинается с @)
        if telegram.startswith('@'):
            return telegram

        # Если ни одно из условий не выполняется, выдаем ошибку
        raise ValidationError(_('Пожалуйста, введите правильный номер телефона или имя пользователя в Telegram.'))

    country = forms.ModelChoiceField(
        label='',
        queryset=Country.objects.all(),
        empty_label="Выберите страну",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_country", "name": "country", }),
    )

    city = forms.ModelChoiceField(
        label='',
        queryset=City.objects.all(),
        empty_label="Выберите город",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_city", "name": "city", }),
        required=False
    )

    image = forms.ImageField(
        # label='',
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-input'}),
        required=False  # Опциональное поле, в зависимости от ваших требований
    )


class ProductFilterForm(forms.ModelForm):
    class Meta:
        model = Films
        fields = ['category', 'sub_category', 'tags', 'country', 'city', 'type']

    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        empty_label='Выберите категорию',
        required=False
    )

    sub_category = forms.ModelChoiceField(
        queryset=SubCategories.objects.all(),
        empty_label='Выберите субкатегорию',
        required=False
    )

    tags = forms.ModelMultipleChoiceField(
        label='',
        queryset=Tag.objects.all(),  # Замените на ваш запрос для выбора тегов
        widget=forms.CheckboxSelectMultiple,  # Используем виджет для выбора нескольких значений
    )

    country = forms.ModelChoiceField(
        label='',
        queryset=Country.objects.all(),
        empty_label="Выберите страну",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_country", "name": "country", }),
        required=False  # Добавляем required=False, чтобы поле не было обязательным
    )

    city = forms.ModelChoiceField(
        label='',
        queryset=City.objects.all(),
        empty_label="Выберите город",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_city", "name": "city", }),
        required=False  # Добавляем required=False, чтобы поле не было обязательным
    )

    TYPE_CHOICES = (
        ('all', 'Все'),
        ('buy', 'Купить'),
        ('sell', 'Продать'),
    )

    type = forms.ChoiceField(
        label='Тип объявления',
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_type', 'name': 'type'}),
        required=False  # Добавляем required=False, чтобы поле не было обязательным
    )

# class ProductFilterForm(forms.Form):
#     category = forms.ModelChoiceField(
#         queryset=Categories.objects.all(),
#         empty_label='Выберите категорию',
#         required=False
#     )
#
#     sub_category = forms.ModelChoiceField(
#         queryset=SubCategories.objects.all(),
#         empty_label='Выберите суб категорию',
#         required=False
#     )
#
#     country = forms.ModelChoiceField(
#         queryset=Country.objects.all(),
#         empty_label='Выберите страну',
#         required=False
#     )
#     city = forms.ModelChoiceField(
#         queryset=City.objects.all(),
#         empty_label='Выберите город',
#         required=False
#     )
#
#     SELL_BUY_CHOICES = [
#         ('all', 'All'),
#         ('sell', 'Sell'),
#         ('buy', 'Buy'),
#     ]
#
#     sell_buy = forms.ChoiceField(
#         choices=SELL_BUY_CHOICES,
#         required=False
#     )
