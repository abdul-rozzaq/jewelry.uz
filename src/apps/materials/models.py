from django.db import models

from apps.common.models import BaseModel


class Material(BaseModel):
    UNIT_CHOICES = [
        ("g", "Gram"),
        ("pcs", "Pieces"),
        ("ct", "Carat"),
    ]

    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    purity = models.DecimalField(max_digits=6, decimal_places=3, default=0)

    def __str__(self):
        return f"{self.name} ({self.unit})"
