from rest_framework import serializers

from apps.materials.serializers import MaterialSerializer
from apps.organizations.serializers import OrganizationSerializer

from .models import OrganizationInventory


class InventoryBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationInventory
        fields = "__all__"


class CreateInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInventory
        fields = ("organization", "material", "quantity")


class GetInventorySerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = OrganizationInventory
        fields = ("id", "organization", "material", "quantity", "created_at", "updated_at")
