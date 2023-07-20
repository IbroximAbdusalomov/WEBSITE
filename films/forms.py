from django import forms

from .models import Films, SubCategories, City


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


class FilmsForm(forms.ModelForm):
    class Meta:
        model = Films
        # create_advertisement = ['author']
        fields = (
            "title",
            "description",
            "telephone",
            # "email",
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
            # "email": forms.TextInput(attrs={
            #     "class": "form-control"
            # }),
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
