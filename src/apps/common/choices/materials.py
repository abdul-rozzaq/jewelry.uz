from django.db import models


class MaterialType(models.TextChoices):
    GOLD_999 = "gold_999", "Gold 999"
    GOLD_585 = "gold_585", "Gold 585"
    IRON = "iron", "Iron"
    IRON_GOLD = "iron_gold", "Iron Gold"
    SCRAP = "scrap", "Scrap"
