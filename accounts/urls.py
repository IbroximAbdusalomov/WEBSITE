from django.urls import path

from . import views

# app_name = 'main'  # -> 'main:app_name'

urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.LogoutUserView.as_view(next_page='index'), name="logout"),
    path("myaccount/", views.MyAccountRedirectView.as_view(), name="myaccount"),
    path("profile/<int:pk>", views.ProfileView.as_view(), name="profile"),

    path("update-profile/", views.UserProfileUpdateView.as_view(), name="update_profile"),

    path("add-company/", views.CreateBusinessAccountView.as_view(), name="create-company"),

    path("product-edit/<int:pk>", views.EditProductsView.as_view(), name="product-edit"),
    path('rate/<int:evaluator_id>/<int:user_id>/<int:grade>/', views.add_rating, name='add_rating'),
    path("notification/", views.notification_list, name="notification"),
    path("send-message/", views.SendNotificationView.as_view(), name="send_message"),
    path('product_phone_view_count/', views.product_phone_view_count, name="product_phone_view_count"),

    path('forgot-password/', views.SendUserDataView.as_view(), name='forgot-password'),
    path('update-password/', views.update_password, name='update-password'),

    path('subscribe/<int:user_id>/', views.subscribe, name='subscribe'),
]
