from django.db import models
from apps.common.models import BaseModel
from apps.organizations.models import Organization
from apps.materials.models import Material


class Transaction(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
    ]

    sender = models.ForeignKey(Organization, related_name="sent_transactions", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Organization, related_name="received_transactions", on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    confirmed_by_sender = models.BooleanField(default=False)
    confirmed_by_receiver = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction {self.id}: {self.sender} → {self.receiver}"


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name="items", on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"
