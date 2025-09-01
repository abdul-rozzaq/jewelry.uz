from django.urls import path

from rest_framework_simplejwt.views import token_refresh

from .views import CustomTokenObtainPairView

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login-view"),
    path("refresh/", token_refresh, name="refresh-view"),
]
