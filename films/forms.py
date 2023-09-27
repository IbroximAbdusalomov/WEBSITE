from django import forms
from django.core.validators import RegexValidator
from django.utils.html import format_html
from django.utils.translation import gettext as _
from .models import Films, City, Country, Categories, SubCategories, Tag


class FilmsForm(forms.ModelForm):
    class Meta:
        model = Films
        fields = ['title', 'description', 'category', 'sub_category', 'tags', 'telegram', 'telephone', 'country',
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

    telegram = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-input', 'placeholder': _('+998 66 666 66 66 или @имя пользователя')}),
        validators=[RegexValidator(
            regex=r'^(\+\d{3} \d{2} \d{3} \d{2} \d{2}|@\w+)$',
            message=_('Введите номер телефона в формате: "+998 66 666 66 66" или имя пользователя, начинающееся с @'),
        )]
    )

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
