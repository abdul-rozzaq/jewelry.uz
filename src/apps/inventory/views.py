from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Mavjud inventory ni tekshirish
            existing_inventory = OrganizationInventory.objects.filter(
                organization=serializer.validated_data["organization"],
                material=serializer.validated_data["material"],
            ).first()

            if existing_inventory:
                # Agar mavjud bo'lsa quantity'ni qo'shish
                existing_inventory.quantity += serializer.validated_data["quantity"]
                existing_inventory.save()
                return Response(
                    self.get_serializer(existing_inventory).data,
                    status=status.HTTP_200_OK,
                )

            # Agar mavjud bo'lmasa yangi yaratish
            return super().create(request, *args, **kwargs)
