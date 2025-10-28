from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Jewelry API",
        default_version="v1",
        description="API documentation for Jewelry",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


api_urls = [
    path("auth/", include("apps.users.urls")),
    path("organizations/", include("apps.organizations.urls")),
    path("transactions/", include("apps.transactions.urls")),
    path("products/", include("apps.products.urls")),
    path("materials/", include("apps.materials.urls")),
    path("processes/", include("apps.processes.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("projects/", include("apps.projects.urls")),
]

urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("admin/", admin.site.urls),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/v1/", include(api_urls)),
    path("drf-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
