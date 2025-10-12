from django.db import models

from apps.common.models import BaseModel


class Project(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
