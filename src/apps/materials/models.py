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

    def __str__(self):
        return f"{self.name} ({self.unit})"
