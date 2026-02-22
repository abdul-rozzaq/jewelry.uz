from rest_framework.decorators import action
from rest_framework.response import Response

from apps.processes.models import CoatProcess
from apps.processes.serializers import (
    CoatProcessSerializer,
    GetCoatProcessSerializer,
)
from apps.processes.serializers.coat_process import CompleteCoatProcessSerializer

from .base import BaseProcessViewSet


class CoatProcessViewSet(BaseProcessViewSet):
    queryset = CoatProcess.objects.all()
    serializer_class = CoatProcessSerializer

    def get_queryset(self):
        return CoatProcess.objects.filter(organization=self.request.user.organization).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        process = self.get_object()

        serializer = self.get_serializer(data=request.data, instance=process)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(self.get_serializer(process).data)

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return GetCoatProcessSerializer

        if self.action == "complete":
            return CompleteCoatProcessSerializer

        return self.serializer_class
