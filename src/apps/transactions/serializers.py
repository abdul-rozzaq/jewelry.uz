from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.products.serializers import ProductReadSerializer


from .models import Transaction, TransactionItem


class TransactionItemSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer()

    class Meta:
        model = TransactionItem
        fields = "__all__"


class GetTransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)

    class Meta:
        model = Transaction
        fields = "__all__"
        depth = 2


class CreateTransactionItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionItem
        fields = ["product", "quantity"]


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
            "project",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items")
        # sender = validated_data["sender"]

        for item in items:
            if item["product"].quantity < item["quantity"]:
                raise ValidationError({"detail": f"{item['product'].material.name} uchun yetarli miqdor yo'q. Mavjud: {item.product.quantity}, so'ralgan {item.quantity}"})

        with transaction.atomic():
            transaction_obj = super().create(validated_data)

            objs = [TransactionItem(transaction=transaction_obj, **item) for item in items]

            TransactionItem.objects.bulk_create(objs)

        return transaction_obj
