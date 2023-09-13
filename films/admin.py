from django.contrib import admin

from .models import Categories, Films, SubCategories, Country, City, Tag


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


admin.site.register(Tag)


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
class FilmsAdmin(admin.ModelAdmin):
    list_display = ("title", "image", "create_date", "update_date", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "sub_category":
            selected_category_id = request.POST.get("category")
            if selected_category_id:
                kwargs["queryset"] = SubCategories.objects.filter(category_id=selected_category_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
