from django.urls import path

from .views import (IndexView, ProductSaveView, FilmsListView, ProductDetailView,
                    related_to_it, add_to_favorites, favorite_list)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("add-film/", ProductSaveView.as_view(), name="add_film"),
    path('product-list/', FilmsListView.as_view(), name='product-list'),

    path('related_to_it/', related_to_it, name='related_to_it'),

    # up to recommendation
    # path('up-to-recommendation/<int:pk>', up_to_recommendation, name='up_to_recommendations'),

    # add del read favorites
    path('add/<int:pk>/', add_to_favorites, name='add_to_favorites'),
    path('favorite_list/', favorite_list, name='favorite_list'),
]
