from rest_framework import viewsets

from .serializers import InventorySerializer
from .models import OrganizationInventory


class InventoryViewset(viewsets.ModelViewSet):
    queryset = OrganizationInventory.objects.all()
    serializer_class = InventorySerializer
    filterset_fields = ["organization"]
