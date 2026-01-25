from asyncio import exceptions
from decimal import ROUND_HALF_UP, Decimal as Q
from django.db import transaction, models


from apps.materials.models import Material
from apps.processes.models import ProcessStatus
from apps.processes.services.base import BaseProcessStrategy
from apps.products.models import Product


class CoatStrategy(BaseProcessStrategy):
    """
    Bu ssenariyda oltin va temir aralashadi.
    faqat oltin (mixes_with_gold=True) purity hisobida ishtirok etadi,
    lekin temir massaga qo‘shiladi.
    Natijada purity kamayadi.
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        inputs = process.inputs.select_related("product__material", "material").select_for_update()
        outputs = process.outputs.select_related("material")

        total_pure_gold = Q("0")
        total_mass = Q("0")

        # === 1) INPUTLAR: oltin miqdorini hisoblash va quantity kamaytirish ===

        for inp in inputs:
            product = inp.product
            material = inp.material or (product.material if product else None)
            qty = Q(inp.quantity)

            if qty <= Q("0"):
                raise exceptions.ValidationError({"detail": f"{material} miqdori musbat bo'lishi kerak."})

            if not material:
                raise exceptions.ValidationError({"detail": "ProcessInput uchun material topilmadi."})

            # faqat mixes_with_gold=True bo'lgan materiallar oltin hisobida qatnashadi

            if material.mixes_with_gold:
                total_pure_gold += qty * Q(material.purity) / Q("100")

            total_mass += qty

            # product mavjud bo‘lsa, quantity ni kamaytirish
            if product:
                if product.quantity < qty:
                    raise exceptions.ValidationError({"detail": f"{product} mahsuloti yetarli emas."})

                product.quantity = (product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
                product.save(update_fields=["quantity"])

        scraps = outputs.filter(material__is_scrap=True).aggregate(total_quantity=models.Sum("quantity"))["total_quantity"] or Q("0")

        scrap_material = outputs.filter(material__is_scrap=True).first().material

        # === 2) OUTPUT: yangi mahsulotni yangilash yoki yaratish ===
        for output in outputs:
            if output.quantity is None or output.quantity <= Q("0"):
                raise exceptions.ValidationError({"detail": "ProcessOutput miqdori musbat bo'lishi kerak."})

            material: Material = output.material

            product, _ = Product.objects.select_for_update().get_or_create(
                organization=process.organization,
                material=material,
                defaults={
                    "quantity": Q("0"),
                    "purity": material.purity,
                    "pure_gold": Q("0"),
                    "is_composite": not material.is_scrap,
                },
            )

            product.quantity = (product.quantity + Q(output.quantity)).quantize(Q("0.0001"))
            product.pure_gold = (product.pure_gold + total_pure_gold - (scraps * (scrap_material.purity / Q("100")))).quantize(Q("0.0001"))

            product.save(update_fields=["quantity", "purity", "pure_gold", "is_composite"])

        # # === 3) PROCESS ni yakunlash ===
        process.total_in = total_pure_gold.quantize(Q("0.0001"))
        process.total_out = total_pure_gold.quantize(Q("0.0001"))
        process.status = ProcessStatus.COMPLETED

        process.save(update_fields=["total_in", "total_out", "status"])

        return process
