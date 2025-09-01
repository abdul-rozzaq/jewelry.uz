from rest_framework.routers import DefaultRouter

from apps.organizations.views import OrganizationViewSet


router = DefaultRouter()

router.register(r"", OrganizationViewSet)

urlpatterns = router.urls + []
