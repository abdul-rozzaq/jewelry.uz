from django.db import models
from apps.common.models import BaseModel
from apps.products.models import Product
from apps.organizations.models import Organization
from apps.projects.models import Project


class TransactionStatuses(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"


class Transaction(BaseModel):
    sender = models.ForeignKey(Organization, related_name="sent_transactions", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Organization, related_name="received_transactions", on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=TransactionStatuses.choices, default=TransactionStatuses.PENDING, db_index=True)

    project = models.ForeignKey(Project, related_name="transactions", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.id}: {self.sender} → {self.receiver}"

    class Meta:
        indexes = [
            models.Index(fields=["sender", "receiver"], name="tx_sender_receiver_idx"),
        ]


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=4)

    def __str__(self):
        return f"{self.product.material.name} - {self.quantity}"

    class Meta:
        indexes = [
            models.Index(fields=["transaction", "product"], name="tx_item_tx_prod_idx"),
        ]
