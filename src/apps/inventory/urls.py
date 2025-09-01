from rest_framework.routers import DefaultRouter

from .views import InventoryViewset

router = DefaultRouter()
router.register(r"", InventoryViewset)


urlpatterns = router.urls + []
