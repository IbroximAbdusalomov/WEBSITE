# support/urls.py
from django.urls import path
from .views import SupportView, SupportSuccessView

urlpatterns = [
    path("", SupportView.as_view(), name="support"),
    path("success/", SupportSuccessView.as_view(), name="support_success"),
]
