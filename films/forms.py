from django import forms
from django.utils.translation import gettext as _

from .models import Films, City, Country, Categories, SubCategories, Tag


class FilmsForm(forms.ModelForm):
    image = forms.ImageField(
        label=_('Изображение'),
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'}))  # Удаляем 'multiple': True

    class Meta:
        model = Films
        fields = ['title', 'description', 'category', 'sub_category', 'tags', 'telephone', 'country', 'city', 'image']

    title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-input'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': _('Введите описание'), 'rows': '4'})
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
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('+998 66 666 66 66')}))

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


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        empty_label='Выберите категорию',
        required=False
    )

    subcategory = forms.ModelChoiceField(
        queryset=SubCategories.objects.all(),
        empty_label='Выберите суб категорию',
        required=False
    )

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label='Выберите страну',
        required=False
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label='Выберите город',
        required=False
    )

    SELL_BUY_CHOICES = [
        ('all', 'All'),
        ('sell', 'Sell'),
        ('buy', 'Buy'),
    ]

    sell_buy = forms.ChoiceField(
        choices=SELL_BUY_CHOICES,
        required=False
    )
