from math import ceil
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
    purity = models.DecimalField(max_digits=6, decimal_places=3, default=0)

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def karat(self):
        return ceil((self.purity / 100) * 24)
