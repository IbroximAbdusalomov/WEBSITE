from django.urls import path
from . import views

# app_name = 'main'  # -> 'main:app_name'

urlpatterns = [
    path("auth/", views.AuthorizationView.as_view(), name="auth"),
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.LogoutUserView.as_view(next_page='index'), name="logout"),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("product-action/", views.ProductActionView.as_view(), name="product-action"),

    path("product-edit/<int:pk>", views.EditProductsView.as_view(), name="product-edit"),

]
