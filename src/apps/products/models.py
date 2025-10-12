from django.db import models, transaction
from django.core.exceptions import ValidationError
from typing import List, Tuple

from apps.common.models import BaseModel
from apps.materials.models import Material
from apps.organizations.models import Organization


class Product(BaseModel):
    """Haqiqiy batch / product instance.

    - `material`: Product turini (Material) bildiradi.
    - `quantity`: ushbu batchdagi umumiy miqdor (masalan, gramda).
    - Genealogiya (tarkib) ProductGenealogy orqali saqlanadi — composition JSON yo'q.
    """

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="products")
    quantity = models.FloatField()
    source_description = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.material.name} ({self.quantity}{self.material.unit})"

    # ----------------------------------------------------------------------
    # Genealogiya bilan ishlovchi yordamchi metodlar
    # ----------------------------------------------------------------------

    def set_genealogy(self, parents: List[Tuple["Material", float]], *, validate: bool = True):

        if validate:
            total = sum(f for _, f in parents)

            if not (0.999 <= total <= 1.001):
                raise ValidationError("Parent fractions must sum to ~1.0")

        self.genealogy_children.all().delete()

        for parent, frac in parents:
            ProductGenealogy.objects.create(product=self, parent=parent, percent=frac)

    @classmethod
    @transaction.atomic
    def create_from_inputs(cls, inputs: List[Tuple["Material", float]], result_material: Material, organization: Organization, source_description: str = None) -> "Product":

        if not inputs:
            raise ValidationError("Inputs are required")

        total_qty = sum(q for _, q in inputs)

        if total_qty <= 0:
            raise ValidationError("Total input quantity must be > 0")

        result = cls.objects.create(
            organization=organization,
            material=result_material,
            quantity=total_qty,
            source_description=source_description,
        )

        for parent, used_qty in inputs:
            frac = used_qty / total_qty
            ProductGenealogy.objects.create(product=result, parent=parent, percent=frac)

        return result

    @transaction.atomic
    def split(self, parts: List[float], *, consume_original: bool = True) -> List["Product"]:

        if not parts:
            raise ValidationError("Parts list is empty")

        total_parts = sum(parts)

        if total_parts <= 0:
            raise ValidationError("Sum of parts must be > 0")

        result_products = []

        for idx, part_qty in enumerate(parts):
            child = Product.objects.create(
                organization=self.organization,
                material=self.material,
                quantity=part_qty,
                source_description=f"Split from {self.id} (part {idx + 1})",
            )
            ProductGenealogy.objects.create(
                product=child,
                parent=self.material,
                percent=(part_qty / self.quantity if self.quantity > 0 else 0),
            )
            result_products.append(child)

        if consume_original:
            self.quantity = max(self.quantity - total_parts, 0)
            self.save(update_fields=["quantity"])

        return result_products



class ProductGenealogy(models.Model):
    """Product o'rtasidagi genealogik aloqani saqlaydi.

    - `product` — child product (natija)
    - `material` — bu productdan olingan input product (Material)
    - `percent` — materialning child ichidagi ulushi (fraction, 0..1)
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="genealogy_parents")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="genealogy_children")

    percent = models.FloatField(help_text="Material contribution as fraction (0..1)")

    class Meta:
        unique_together = ("product", "material")

    def __str__(self) -> str:
        pct = round(self.percent * 100, 4)
        return f"{self.material.name} -> {self.product.material.name} ({pct}%)"
