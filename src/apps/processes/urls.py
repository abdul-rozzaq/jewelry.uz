from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.specific_process import CoatProcessViewSet, GoldDowngradeProcessViewSet

router = DefaultRouter()
router.register(r"coat", CoatProcessViewSet, basename="coat-process")
router.register(r"gold-downgrade", GoldDowngradeProcessViewSet, basename="gold-downgrade-process")

urlpatterns = [
    path("", include(router.urls)),
]
