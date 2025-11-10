from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction

from apps.users.models import User, UserRoles

from .serializers import ProductReadSerializer, ProductWriteSerializer
from .models import Product

from operator import itemgetter


class ProductsViewset(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("material", "organization", "project").all()
    serializer_class = ProductReadSerializer
    filterset_fields = ["organization", "is_composite"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return ProductWriteSerializer

        return ProductReadSerializer

    def get_queryset(self):
        user: User = self.request.user

        queryset = super().get_queryset().order_by("material__name")

        if not user.is_authenticated:
            return queryset.none()

        if user.role == UserRoles.ADMIN or user.is_superuser or user.is_staff:
            return queryset

        return queryset.filter(organization=user.organization)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        organization = request.user.organization

        material, quantity = itemgetter("material", "quantity")(data)
        project = data.get("project", None)

        existing_product = Product.objects.select_for_update().filter(
            organization=organization,
            project=project,
            material=material,
        ).first()

        if existing_product:
            existing_product.quantity += quantity
            existing_product.save(update_fields=["quantity"])

            return Response(self.get_serializer(existing_product).data, status=status.HTTP_200_OK)

        product = serializer.save(organization=organization)

        return Response(self.get_serializer(product).data, status=status.HTTP_201_CREATED)
