from django.contrib import admin

from .models import Categories, Films, SubCategories, Country, City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


#
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


#
@admin.register(SubCategories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(Films)
class FilmsAdmin(admin.ModelAdmin):  # Представление модели в админке
    # Параметр отображения полей для Модели
    list_display = ("title", "image", "create_date", "update_date", "is_published")
