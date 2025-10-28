from django.db import models

from apps.common.models import BaseModel
from apps.materials.models import Material
from apps.organizations.models import Organization
from apps.projects.models import Project


class Product(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="products")
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    purity = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    source_description = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.material.name} ({self.quantity}{self.material.unit})"

    @property
    def karat(self):
        from math import ceil

        return ceil((self.purity / 100) * 24)
