from django.urls import path

from .views import DashboardStatisticsAPIView

urlpatterns = [
    path("stats/", DashboardStatisticsAPIView.as_view(), name="dashboard-stats"),
]
