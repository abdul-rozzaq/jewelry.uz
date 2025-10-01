from rest_framework import serializers

from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), source="organization", write_only=True)
    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), source="material", write_only=True)

    organization = OrganizationSerializer(read_only=True)
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "organization_id",
            "material_id",
            "organization",
            "material",
            "quantity",
            "created_at",
            "updated_at",
        )
