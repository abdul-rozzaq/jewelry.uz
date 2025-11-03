from django.db import models

from apps.common.models import BaseModel
from apps.materials.models import Material
from apps.organizations.models import Organization
from apps.projects.models import Project


class Product(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="products")
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    purity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    is_composite = models.BooleanField(
        default=False,
        help_text="Indicates if product contains non-gold materials (e.g., iron core).",
    )
    pure_gold = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        help_text="Actual mass of pure gold within this product in grams.",
    )
    source_description = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        extra = []

        if self.is_composite:
            extra.append("composite")

        if self.pure_gold:
            extra.append(f"Au {self.pure_gold}g")
        extra_str = f" | {'; '.join(extra)}" if extra else ""

        return f"{self.material.name} ({self.quantity}{self.material.unit}){extra_str}"

    @property
    def karat(self):
        from math import ceil

        return ceil((self.purity / 100) * 24)

    # def save(self, *args, **kwargs):
    #     # Auto-calculate pure_gold for non-composite items using product purity
    #     if not self.is_composite:
    #         try:
    #             # quantity: 4 dp; purity: 3 dp -> pure_gold: 3 dp
    #             raw = (Decimal(self.quantity) * Decimal(self.purity)) / Decimal("100")
    #             self.pure_gold = raw.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    #         except Exception:
    #             # In case of any casting issue, fall back gracefully (won't validate here)
    #             pass

    #     super().save(*args, **kwargs)
