from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.processes.models import CoatProcess, GoldDowngradeProcess
from apps.processes.serializers.specific_process import CoatProcessSerializer, GoldDowngradeProcessSerializer


class CoatProcessViewSet(viewsets.ModelViewSet):
    queryset = CoatProcess.objects.all()
    serializer_class = CoatProcessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoatProcess.objects.filter(organization=self.request.user.organization).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class GoldDowngradeProcessViewSet(viewsets.ModelViewSet):
    queryset = GoldDowngradeProcess.objects.all()
    serializer_class = GoldDowngradeProcessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoldDowngradeProcess.objects.filter(organization=self.request.user.organization).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
