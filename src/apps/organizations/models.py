from django.db import models

from apps.common.models import BaseModel


class OrganizationType(models.TextChoices):
    gold_processing   = "gold_processing"  , "Oltin qayta ishlash"
    silver_processing = "silver_processing", "Kumush qayta ishlash"
    jewelry_making    = "jewelry_making"   , "Zargarlik buyumlari yaratish"
    cleaning          = "cleaning"         , "Tozalash"
    repair            = "repair"           , "Ta'mirlash"
    bank              = "bank"             , "Bank"


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=OrganizationType.choices)

    def __str__(self):
        return f"{self.name} ({self.type})"
