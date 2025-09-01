from django.db import models

from apps.common.models import BaseModel


class Organization(BaseModel):
    ORG_TYPES = [
        ("bank", "Bank"),
        ("atolye", "Atolye"),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ORG_TYPES)

    def __str__(self):
        return f"{self.name} ({self.type})"
