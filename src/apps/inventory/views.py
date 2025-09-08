from rest_framework import viewsets

from apps.users.models import User, UserRoles

from .serializers import InventorySerializer
from .models import OrganizationInventory


class InventoryViewset(viewsets.ModelViewSet):
    queryset = OrganizationInventory.objects.none()
    serializer_class = InventorySerializer
    filterset_fields = ["organization"]

    def get_queryset(self):
        user: User = self.request.user

        if user.role == UserRoles.ADMIN:
            return OrganizationInventory.objects.all()

        return OrganizationInventory.objects.filter(organization=user.organization)
