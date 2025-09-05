from rest_framework import viewsets

from .serializers import CreateInventorySerializer, GetInventorySerializer
from .models import OrganizationInventory


class InventoryViewset(viewsets.ModelViewSet):
    queryset = OrganizationInventory.objects.all()
    serializer_class = CreateInventorySerializer
    filterset_fields = ["organization"]

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:
            return GetInventorySerializer

        return self.serializer_class
