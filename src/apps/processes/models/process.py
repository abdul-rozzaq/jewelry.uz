from django.db import models

from apps.common.models import BaseModel
from apps.materials.models import Material
from apps.organizations.models import Organization
from apps.products.models import Product
from apps.projects.models import Project

from .process_type import ProcessType


class ProcessStatus(models.TextChoices):
    IN_PROCESS = "in process", "In process"
    COMPLETED = "completed", "Completed"


class Process(BaseModel):
    project = models.ForeignKey(Project, related_name="processes", on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    process_type = models.ForeignKey(ProcessType, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=64, choices=ProcessStatus.choices, default=ProcessStatus.IN_PROCESS, db_index=True)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    total_in = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    total_out = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"
        indexes = [
            models.Index(fields=["organization", "status"], name="proc_org_status_idx"),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.process_type} ({self.id})"


class ProcessInput(models.Model):
    process = models.ForeignKey(Process, related_name="inputs", on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=4, null=True)

    def __str__(self):
        return f"Input {self.product} {self.material} - {self.quantity}"


class ProcessOutput(models.Model):
    process = models.ForeignKey(Process, related_name="outputs", on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=4, null=True)

    def __str__(self):
        return f"Output {self.material.name} - {self.quantity}"
