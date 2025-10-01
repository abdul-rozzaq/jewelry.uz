from rest_framework.routers import DefaultRouter

from .views import ProductsViewset

router = DefaultRouter()
router.register(r"", ProductsViewset)


urlpatterns = router.urls + []
