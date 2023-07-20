import django_filters
from .models import Films


class CategoryFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter(field_name='category', lookup_expr='exact')

    class Meta:
        model = Films
        fields = ['category']  # Замените 'slug' на поле, по которому хотите фильтровать


class SubCategoryFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter(field_name='sub_category', lookup_expr='exact')

    class Meta:
        model = Films
        fields = ['sub_category']  # Замените 'slug' на поле, по которому хотите фильтровать
