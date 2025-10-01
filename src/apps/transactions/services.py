from django.db import transaction as db_transaction

from rest_framework.exceptions import ValidationError

from apps.products.models import Product
from apps.transactions.models import Transaction, TransactionStatuses


class TransactionService:

    @staticmethod
    def accept_transaction(transaction: Transaction):
        if transaction.status == TransactionStatuses.ACCEPTED:
            raise ValidationError({"detail": f"{transaction} allaqachon tasdiqlangan"})

        items = transaction.items.select_related("product", "product__material").all()
        receiver = transaction.receiver

        with db_transaction.atomic():
            for item in items:
                if item.product.quantity < item.quantity:
                    raise ValidationError({"detail": f"{item.product.material.name} uchun yetarli miqdor yo‘q. " f"Mavjud: {item.product.quantity}, so‘ralgan: {item.quantity}"})

            for item in items:
                sender_product = item.product
                sender_product.quantity -= item.quantity
                sender_product.save(update_fields=["quantity"])

                receiver_product, _ = Product.objects.get_or_create(organization=receiver, material=sender_product.material, defaults={"quantity": 0})
                receiver_product.quantity += item.quantity
                receiver_product.save(update_fields=["quantity"])

            transaction.status = TransactionStatuses.ACCEPTED
            transaction.save(update_fields=["status"])

        return transaction
