from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("subscribe/", views.SubscribePushView.as_view(), name="subscribe-push"),
    path("unsubscribe/", views.UnsubscribePushView.as_view(), name="unsubscribe-push"),
    path("<int:pk>/mark-as-read/", views.MarkAsReadView.as_view(), name="mark-as-read"),
    path("", views.NotificationListView.as_view(), name="list"),
]
