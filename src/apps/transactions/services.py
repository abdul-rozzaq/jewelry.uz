from django.db import transaction as db_transaction

from rest_framework.exceptions import ValidationError

from apps.inventory.models import OrganizationInventory
from apps.transactions.models import Transaction, TransactionStatuses


class TransactionService:
    @staticmethod
    def accept_transaction(transaction: Transaction):
        if transaction.status == TransactionStatuses.ACCEPTED:
            raise ValidationError({"detail": f"{transaction} allaqachon tasdiqlangan"})

        items = transaction.items.select_related("inventory", "inventory__material").all()
        receiver = transaction.receiver

        with db_transaction.atomic():
            for item in items:
                if item.inventory.quantity < item.quantity:
                    raise ValidationError({"detail": f"{item.inventory.material.name} uchun yetarli miqdor yo‘q. " f"Mavjud: {item.inventory.quantity}, so‘ralgan: {item.quantity}"})

            for item in items:
                sender_inventory = item.inventory
                sender_inventory.quantity -= item.quantity
                sender_inventory.save(update_fields=["quantity"])

                receiver_inventory, _ = OrganizationInventory.objects.get_or_create(organization=receiver, material=sender_inventory.material, defaults={"quantity": 0})
                receiver_inventory.quantity += item.quantity
                receiver_inventory.save(update_fields=["quantity"])

            transaction.status = TransactionStatuses.ACCEPTED
            transaction.save(update_fields=["status"])

        return transaction
