from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProcessCreateApiView, ProcessListApiView

# from apps.processes.views import ProcessViewSet


router = DefaultRouter()

# router.register("", ProcessViewSet)


urlpatterns = router.urls + [
    path("list/", ProcessListApiView.as_view(), name="process-list"),
    path("create/", ProcessCreateApiView.as_view(), name="process-create"),
]
