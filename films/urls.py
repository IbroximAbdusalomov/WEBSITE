from django.urls import path

from .views import (IndexView, ProductSaveView, FilmsListView, ProductDetailView,
                    related_to_it, add_to_favorite, remove_from_favorite)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("add-film/", ProductSaveView.as_view(), name="add_film"),
    path('product-list/', FilmsListView.as_view(), name='product-list'),

    path('related_to_it/', related_to_it, name='related_to_it'),

    # up to recommendation
    # path('up-to-recommendation/<int:pk>', up_to_recommendation, name='up_to_recommendations'),

    path('add/<int:pk>/', add_to_favorite, name='add_to_favorite'),
    path('remove/<int:pk>/', remove_from_favorite, name='remove_from_favorite'),
]
