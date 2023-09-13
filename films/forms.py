from django import forms
from .models import Films, SubCategories, City, Country, Categories, Tag
from django.utils.translation import gettext as _


class PersonCreationForm(forms.ModelForm):
    class Meta:
        model = Films
        fields = ["country", "city", "category", "sub_category"]

        labels = {
            # "country": '',
            # "city": '',
            # 'category': '',
            # 'sub_category': '',
        }

        widgets = {
            "country": forms.Select(attrs={
                "class": "form-select"
            }),
            "city": forms.Select(attrs={
                "class": "form-select",
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "sub_category": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategories.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategories.objects.filter(category_id=category_id).order_by(
                    'name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['sub_category'].queryset = self.instance.category.sub_category_set.order_by('name')

        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')


class FilmsFormBUY(forms.ModelForm):
    class Meta:
        model = Films
        # create_advertisement = ['author']
        fields = (
            "title",
            "description",
            "telephone",
            "image",
            "country",
            "city",
            "category",
            "sub_category",
            "is_published",
        )
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),
            "telephone": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "price": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "image": forms.FileInput(attrs={
                "class": "form-control"
            }),
            "country": forms.Select(attrs={
                "class": "form-select"
            }),
            "city": forms.Select(attrs={
                "class": "form-select"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "sub_category": forms.Select(attrs={
                "class": "form-select"
            }),
            "is_published": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategories.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategories.objects.filter(category_id=category_id).order_by(
                    'name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['sub_category'].queryset = self.instance.category.sub_category_set.order_by('name')

        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')


class FilmsFormSELL(forms.ModelForm):
    class Meta:
        model = Films
        # create_advertisement = ['author']
        fields = (
            "title",
            "description",
            "telephone",
            "price",
            "image",
            "country",
            "city",
            "category",
            "sub_category",
            "is_published",
        )

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),
            "telephone": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "price": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "image": forms.FileInput(attrs={
                "class": "form-control"
            }),
            "country": forms.Select(attrs={
                "class": "form-select"
            }),
            "city": forms.Select(attrs={
                "class": "form-select"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "sub_category": forms.Select(attrs={
                "class": "form-select"
            }),
            "is_published": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategories.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategories.objects.filter(category_id=category_id).order_by(
                    'name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['sub_category'].queryset = self.instance.category.sub_category_set.order_by('name')

        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')


class EditFilmForm(forms.ModelForm):
    class Meta:

        model = Films
        fields = [
            "title",
            "description",
            "price",
            "image",
            "category",
            "sub_category",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),
            "price": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),
            "image": forms.FileInput(attrs={
                "class": "form-control"
            }),
            "country": forms.Select(attrs={
                "class": "form-select"
            }),
            "city": forms.Select(attrs={
                "class": "form-select"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "sub_category": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategories.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategories.objects.filter(
                    category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['sub_category'].queryset = self.instance.category.sub_category_set.order_by('name')
        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')


class FilmFilterForm(forms.Form):
    country = forms.CharField(required=False)
    city = forms.CharField(required=False)
    category = forms.CharField(required=False)
    sub_category = forms.CharField(required=False)


class FilmForm(forms.Form):
    name = forms.CharField(
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
        max_length=255  # Максимальная длина названия
    )
    description = forms.CharField(
        label='Описание',
        widget=forms.Textarea(attrs={'class': 'form-textarea'}),
        required=True
    )
    category = forms.ChoiceField(
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        choices=[
            ('', 'Выберите категорию'),
            ('yangi uskunalar', 'Yangi uskunalar'),
            ('ishlatilgan uskunalar', 'Ishlatilgan uskunalar'),
            ('xom ashyo', 'Xom ashyo'),
            ('xizmat ko\'rsatish', 'Xizmat ko\'rsatish'),
            ('texnolog', 'Texnolog'),
            # Другие варианты категорий
        ]
    )
    subcategory = forms.ChoiceField(
        label='Субкатегория',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        choices=[
            ('', 'Выберите субкатегорию'),
            ('Субкатегория 1', 'Субкатегория 1'),
            ('Субкатегория 2', 'Субкатегория 2'),
            # Другие варианты субкатегорий
        ]
    )
    phone = forms.CharField(
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True
    )


class FilmsForm(forms.ModelForm):
    class Meta:
        model = Films
        fields = ['title', 'description', 'category', 'sub_category', 'tags', 'telephone', 'country', 'city']

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


class CategoryForm(forms.Form):
    university = forms.ModelChoiceField(
        label='',
        queryset=Categories.objects.all(),
        empty_label="Выберите категорию",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_category", "name": "category", }),
    )


class SubCategoryForm(forms.Form):
    sub_category = forms.ModelChoiceField(
        label='',
        queryset=SubCategories.objects.all(),
        empty_label="Выберите субкатегорию",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-select', "id": "id_sub_category", "name": "sub_category"}),
    )


class TagForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        label='',
        queryset=Tag.objects.all(),  # Замените на ваш запрос для выбора тегов
        widget=forms.CheckboxSelectMultiple,  # Используем виджет для выбора нескольких значений
    )

    # class Meta:
    #     model = Tag
    #     fields = ['name', 'tags']
