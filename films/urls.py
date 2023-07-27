from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("category/<slug:slug>", views.FilmFilterView.as_view(), name="category_detail"),
    path("film/<int:pk>/", views.FilmDetailView.as_view(), name="film_detail"),
    path("search/", views.FilmsSearchView.as_view(), name="search"),
    path("add-film/", views.FilmBuyView.as_view(), name="add_film"),
    path("sell-film/", views.FilmSellView.as_view(), name="sell_film"),
    path('edit/<int:pk>', views.FilmEditView.as_view(), name="edit_film"),
    path("delete-film/<int:pk>/", views.FilmDeleteView.as_view(), name="delete_film"),

    # send to bot
    # path("upload", views.my_view, name='upload'),
    # path("sell", views.my_view, name='kuku'),

    # category
    path('ajax/load-sub-categories/', views.load_categories, name='ajax_load_sub_categories'),
    # path('add-film/load-cities/', views.load_categories, name='ajax_load_cities_1'),

    # country
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    # path('ajax/load-cities/', views.load_categories, name='ajax_load_cities'),

    # categorise in navbar
    # path('category/<str:slug>', views.filter_category, name='category_detail'),

    # product list
    path('buy-page', views.BuyView.as_view(), name='buy'),
    path('sell-page', views.SellView.as_view(), name='sell'),

    # up to recommendation
    path('up-to-recommendation/<int:pk>', views.up_to_recommendation, name='up_to_recommendations'),

    path('add/<int:product_id>/', views.add_to_favorite, name='add_to_favorite'),
    # Удаление объекта из избранного
    path('remove/<int:product_id>/', views.remove_from_favorite, name='remove_from_favorite'),

    path('favorites', views.my_favorite_list, name='favo'),

]
