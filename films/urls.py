from django.urls import path

# from .views import (IndexView, ProductFilterView,
#                     ProductDetailView,
#                     ProductsSearchView,
#                     ProductBuyView,
#                     ProductSellView,
#                     ProductEditView,
#                     ProductDeleteView, related_to_it, load_cities, BuyView, SellView, add_to_favorite,
#                     remove_from_favorite, my_favorite_list)

from .views import (IndexView, ProductSaveView, FilmsListView, FilterProductsView,
                    related_to_it, load_cities, add_to_favorite, remove_from_favorite, my_favorite_list)

urlpatterns = [

    path("", IndexView.as_view(), name="index"),
    path("filter-products/", FilterProductsView.as_view(), name="filter-products"),
    # path("film/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    # path("search/", ProductsSearchView.as_view(), name="search"),
    path("add-film/", ProductSaveView.as_view(), name="add_film"),
    # path('edit/<int:pk>', ProductEditView.as_view(), name="edit_film"),
    # path("delete-film/<int:pk>/", ProductDeleteView.as_view(), name="delete_film"),
    path('product-list/', FilmsListView.as_view(), name='product-list'),
    # category
    path('related_to_it/', related_to_it, name='related_to_it'),

    # country
    path('ajax/load-cities/', load_cities, name='ajax_load_cities'),

    # product list
    # path('buy-page', BuyView.as_view(), name='buy'),
    # path('sell-page', SellView.as_view(), name='sell'),

    # up to recommendation
    # path('up-to-recommendation/<int:pk>', up_to_recommendation, name='up_to_recommendations'),

    path('add/<int:product_id>/', add_to_favorite, name='add_to_favorite'),
    # Удаление объекта из избранного
    path('remove/<int:product_id>/', remove_from_favorite, name='remove_from_favorite'),

    path('favorites', my_favorite_list, name='favo'),

]
