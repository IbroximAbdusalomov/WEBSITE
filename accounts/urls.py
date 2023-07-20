from django.urls import path
from . import views

# app_name = 'main'  # -> 'main:app_name'

urlpatterns = [
    path("auth/", views.AuthorizationView.as_view(), name="auth"),
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.LogoutUserView.as_view(), name="logout"),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("users/<int:pk>", views.delete_confirm, name="del"),
    path("users/users/<int:pk>", views.delete_film, name="del1"),
    path("edit-profile/<int:pk>/", views.EditProfileView.as_view(), name="edit_profile"),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
]
