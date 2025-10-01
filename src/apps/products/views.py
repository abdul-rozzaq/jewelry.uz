from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction

from apps.users.models import User, UserRoles
from .serializers import ProductSerializer
from .models import Product


class ProductsViewset(viewsets.ModelViewSet):
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    filterset_fields = ["organization"]

    def get_queryset(self):
        user: User = self.request.user

        if not user.is_authenticated:
            return self.queryset

        if user.role == UserRoles.ADMIN:
            return Product.objects.all()

        return Product.objects.filter(organization=user.organization)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            existing_product = Product.objects.filter(
                organization=serializer.validated_data["organization"],
                material=serializer.validated_data["material"],
            ).first()

            if existing_product:
                existing_product.quantity += serializer.validated_data["quantity"]
                existing_product.save()
                return Response(
                    self.get_serializer(existing_product).data,
                    status=status.HTTP_200_OK,
                )

            return super().create(request, *args, **kwargs)
