from rest_framework import serializers

from .models import OrganizationInventory


class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationInventory
        fields = "__all__"
