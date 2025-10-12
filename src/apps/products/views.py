from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction

from apps.users.models import User, UserRoles

from .serializers import ProductGenealogySerializer, ProductSerializer
from .models import Product

from operator import itemgetter


class ProductsViewset(viewsets.ModelViewSet):
    """ProductViewset — mahsulotlar bilan CRUD amallarni bajaradi.

    - Admin barcha mahsulotlarni ko‘ra oladi.
    - Oddiy foydalanuvchi faqat o‘z tashkiloti mahsulotlarini ko‘radi.
    - Yangi product yaratilganda, agar shu material va tashkilot uchun mavjud bo‘lsa, miqdor qo‘shiladi.
    - Genealogiya ma’lumotlari bo‘lsa, ular `ProductGenealogy` orqali saqlanadi.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ["organization"]

    def get_queryset(self):
        user: User = self.request.user

        if not user.is_authenticated:
            return Product.objects.none()

        if user.role == UserRoles.ADMIN or user.is_superuser or user.is_staff:
            return Product.objects.all()

        return Product.objects.filter(organization=user.organization)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        organization = request.user.organization

        material, quantity = itemgetter("material", "quantity")(data)

        genealogy_data = request.data.get("genealogy", [])

        existing_product = Product.objects.filter(
            organization=organization,
            material=material,
        ).first()

        if existing_product:
            existing_product.quantity += quantity
            existing_product.save(update_fields=["quantity"])

            return Response(self.get_serializer(existing_product).data, status=status.HTTP_200_OK)

        product = serializer.save(organization=organization)

        if genealogy_data:
            genealogy_serializer = ProductGenealogySerializer(data=genealogy_data, many=True)
            genealogy_serializer.is_valid(raise_exception=True)
            genealogy_serializer.save(product=product)

        return Response(self.get_serializer(product).data, status=status.HTTP_201_CREATED)
