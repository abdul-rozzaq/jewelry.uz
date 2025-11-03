from django.db import models

from apps.common.models import BaseModel
from apps.organizations.models import Organization
from apps.materials.models import Material
from apps.products.models import Product
from apps.projects.models import Project


class ProcessStatus(models.TextChoices):
    IN_PROCESS = "in process", "In process"
    COMPLETED = "completed", "Completed"


class ProcessTypes(models.TextChoices):
    MELTING = "melting", "Melting"
    POLISHING = "polishing", "Polishing"
    CASTING = "casting", "Casting"
    MIXING = "mixing", "Mixing"
    CUTTING = "cutting", "Cutting"
    ASSEMBLING = "assembling", "Assembling"
    TESTING = "testing", "Testing"
    PACKAGING = "packaging", "Packaging"


class ProcessTemplate(models.Model):
    name = models.CharField(max_length=256)

    inputs = models.ManyToManyField(Material, related_name="template_inputs")
    outputs = models.ManyToManyField(Material, related_name="template_outputs")

    def __str__(self):
        return f"Template(name={self.name})"


def default_name():
    return {"uz": "", "en": "", "tr": ""}


class ProcessType(models.Model):
    name = models.JSONField(default=default_name)
    type = models.CharField(max_length=64, choices=ProcessTypes.choices, default=ProcessTypes.MIXING)
    template = models.ForeignKey(ProcessTemplate, null=True, blank=True, on_delete=models.SET_NULL)

    def get_name(self, lang="en"):
        """Tilga qarab nomni qaytaradi. Agar mavjud bo‘lmasa, type nomini beradi."""
        return self.name.get(lang) or self.get_type_display()

    def __str__(self):
        return self.get_name("uz")


class Process(BaseModel):
    project = models.ForeignKey(Project, related_name="processes", on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    process_type = models.ForeignKey(ProcessType, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=64, choices=ProcessStatus.choices, default=ProcessStatus.IN_PROCESS)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    total_in = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    total_out = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"

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
