from apps.processes.models import GoldDowngradeProcess
from apps.processes.serializers import (
    GoldDowngradeProcessSerializer,
)

from .base import BaseProcessViewSet


class GoldDowngradeProcessViewSet(BaseProcessViewSet):
    queryset = GoldDowngradeProcess.objects.all()
    serializer_class = GoldDowngradeProcessSerializer

    def get_queryset(self):
        return GoldDowngradeProcess.objects.filter(organization=self.request.user.organization).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
