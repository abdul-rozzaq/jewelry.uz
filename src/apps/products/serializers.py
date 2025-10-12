from rest_framework import serializers

from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from apps.organizations.serializers import OrganizationSerializer

from .models import Product, ProductGenealogy


class ProductGenealogySerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), source="material", write_only=True)

    class Meta:
        model = ProductGenealogy
        fields = ("percent", "material", "material_id")


class ProductSerializer(serializers.ModelSerializer):
    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), source="material", write_only=True)

    organization = OrganizationSerializer(read_only=True)
    material = MaterialSerializer(read_only=True)

    genealogy_parents = ProductGenealogySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "material_id",
            "organization",
            "material",
            "quantity",
            "genealogy_parents",
            "created_at",
            "updated_at",
        )
