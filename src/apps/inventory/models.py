from django.db import models

from apps.common.models import BaseModel
from apps.materials.models import Material
from apps.organizations.models import Organization


class OrganizationInventory(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    def __str__(self):
        return f"{self.organization.name} - {self.material.name}: {self.quantity}"
