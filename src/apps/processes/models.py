from django.db import models

from apps.common.models import BaseModel
from apps.organizations.models import Organization
from apps.materials.models import Material


class Process(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    process_type = models.CharField(max_length=128, null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"

    def __str__(self):
        return f"{self.organization.name} - {self.process_type} ({self.id})"


class ProcessInput(models.Model):
    process = models.ForeignKey(Process, related_name="inputs", on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)

    def __str__(self):
        return f"Input {self.material.name} - {self.quantity}"


class ProcessOutput(models.Model):
    process = models.ForeignKey(Process, related_name="outputs", on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)

    def __str__(self):
        return f"Output {self.material.name} - {self.quantity}"
