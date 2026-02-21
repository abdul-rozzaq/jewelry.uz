from rest_framework.response import Response
from rest_framework.decorators import action

from apps.processes.models import CoatProcess, GoldDowngradeProcess
from apps.processes.serializers import (
    CoatProcessSerializer,
    GoldDowngradeProcessSerializer,
    GetCoatProcessSerializer,
)


from .base import BaseProcessViewSet


class CoatProcessViewSet(BaseProcessViewSet):
    queryset = CoatProcess.objects.all()
    serializer_class = CoatProcessSerializer

    def get_queryset(self):
        return CoatProcess.objects.filter(organization=self.request.user.organization).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        process = self.get_object()
        process.finish()
        return Response(self.get_serializer(process).data)

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return GetCoatProcessSerializer

        return self.serializer_class


class GoldDowngradeProcessViewSet(BaseProcessViewSet):
    queryset = GoldDowngradeProcess.objects.all()
    serializer_class = GoldDowngradeProcessSerializer

    def get_queryset(self):
        return GoldDowngradeProcess.objects.filter(organization=self.request.user.organization).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
