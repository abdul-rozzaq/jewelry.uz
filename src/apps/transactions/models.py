from django.db import models
from apps.common.models import BaseModel
from apps.inventory.models import OrganizationInventory
from apps.organizations.models import Organization


class TransactionStatuses(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"


class Transaction(BaseModel):

    sender = models.ForeignKey(Organization, related_name="sent_transactions", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Organization, related_name="received_transactions", on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=TransactionStatuses.choices, default=TransactionStatuses.PENDING)

    def __str__(self):
        return f"Transaction {self.id}: {self.sender} → {self.receiver}"


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name="items", on_delete=models.CASCADE)
    inventory = models.ForeignKey(OrganizationInventory, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)

    def __str__(self):
        return f"{self.inventory.material.name} - {self.quantity}"
