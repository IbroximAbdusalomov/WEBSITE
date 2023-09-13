from django.urls import path
from .views import (IndexView, ProductFilterView, ProductDetailView, ProductsSearchView, ProductBuyView,
                    ProductSellView, ProductEditView, ProductDeleteView, load_cities, related_to_it, BuyView,
                    SellView,
    #  up_to_recommendation,
                    add_to_favorite, remove_from_favorite, my_favorite_list)

urlpatterns = [

    path("", IndexView.as_view(), name="index"),
    path("category/<slug:slug>", ProductFilterView.as_view(), name="category_detail"),
    path("film/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("search/", ProductsSearchView.as_view(), name="search"),
    path("add-film/", ProductBuyView.as_view(), name="add_film"),
    path("sell-film/", ProductSellView.as_view(), name="sell_film"),
    path('edit/<int:pk>', ProductEditView.as_view(), name="edit_film"),
    path("delete-film/<int:pk>/", ProductDeleteView.as_view(), name="delete_film"),

    # category
    path('related_to_it/', related_to_it, name='related_to_it'),

    # country
    path('ajax/load-cities/', load_cities, name='ajax_load_cities'),

    # product list
    path('buy-page', BuyView.as_view(), name='buy'),
    path('sell-page', SellView.as_view(), name='sell'),

    # up to recommendation
    # path('up-to-recommendation/<int:pk>', up_to_recommendation, name='up_to_recommendations'),

    path('add/<int:product_id>/', add_to_favorite, name='add_to_favorite'),
    # Удаление объекта из избранного
    path('remove/<int:product_id>/', remove_from_favorite, name='remove_from_favorite'),

    path('favorites', my_favorite_list, name='favo'),

]
