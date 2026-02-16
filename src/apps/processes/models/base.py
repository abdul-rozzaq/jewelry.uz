from django.db import models
from apps.common.models import BaseModel
from apps.organizations.models import Organization
from apps.projects.models import Project


class ProcessStatus(models.TextChoices):
    IN_PROCESS = "in_process", "Jarayonda"
    COMPLETED = "completed", "Yakunlandi"
    CANCELED = "canceled", "Bekor qilindi"


class BaseProcess(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name="%(class)ss", on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=64, choices=ProcessStatus.choices, default=ProcessStatus.IN_PROCESS, db_index=True)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    total_in = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    total_out = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)

    class Meta:
        abstract = True
