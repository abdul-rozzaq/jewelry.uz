from rest_framework import serializers

from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from apps.organizations.serializers import OrganizationSerializer
from apps.projects.serializers import ProjectSerializer
from apps.projects.models import Project

from .models import Product


class ProductWriteSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), source="project", write_only=True, required=False, allow_null=True)
    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), source="material", write_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "material_id",
            "project_id",
            "quantity",
            "purity",
            "source_description",
        )

    def save(self, **kwargs):
        product = super().save(**kwargs)

        product.purity = product.material.purity
        product.save(update_fields=["purity"])

        return product


class ProductReadSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    material = MaterialSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    karat = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "organization",
            "project",
            "material",
            "quantity",
            "purity",
            "karat",
            "source_description",
            "project",
            "created_at",
            "updated_at",
        )

    def get_karat(self, obj):
        return obj.karat
