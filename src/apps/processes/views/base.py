from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class BaseProcessViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        process = self.get_object()
        process.finish()
        return Response(self.get_serializer(process).data)
