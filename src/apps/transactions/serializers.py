from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.inventory.serializers import InventorySerializer
from apps.organizations.serializers import OrganizationSerializer


from .models import Transaction, TransactionItem


class TransactionItemSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer()

    class Meta:
        model = TransactionItem
        fields = "__all__"


class GetTransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)

    sender = OrganizationSerializer()
    receiver = OrganizationSerializer()

    class Meta:
        model = Transaction
        fields = "__all__"


class CreateTransactionItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionItem
        fields = ["inventory", "quantity"]


class CreateTransactionSerializer(serializers.ModelSerializer):
    items = CreateTransactionItemSerializer(many=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "sender",
            "receiver",
            "status",
            "items",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items")
        # sender = validated_data["sender"]

        for item in items:

            # if item["inventory"].organization != sender:
            #     raise ValidationError({"detail": f"{item['inventory']} bu {sender} ga tegishli emas"})

            if item["inventory"].quantity < item["quantity"]:
                raise ValidationError({"detail": f"{item['inventory'].material.name} uchun yetarli miqdor yo'q. Mavjud: {item.inventory.quantity}, so'ralgan {item.quantity}"})

        with transaction.atomic():
            transaction_obj = super().create(validated_data)

            objs = [TransactionItem(transaction=transaction_obj, **item) for item in items]

            TransactionItem.objects.bulk_create(objs)

        return transaction_obj
