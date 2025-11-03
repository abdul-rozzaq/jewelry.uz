from decimal import Decimal as Q, ROUND_HALF_UP
from django.db import transaction

from rest_framework import exceptions

from apps.processes.services.base import BaseProcessStrategy
from apps.products.models import Product
from apps.processes.models import ProcessOutput, ProcessStatus


class MixingStrategy(BaseProcessStrategy):
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

            # product mavjud bo‘lsa, quantity ni kamaytirish
            if product:
                if product.quantity < qty:
                    raise exceptions.ValidationError({"detail": f"{product} mahsuloti yetarli emas."})

                product.quantity = (product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
                product.save(update_fields=["quantity"])

        # === 2) OUTPUT: yangi mahsulotni yangilash yoki yaratish ===
        output: ProcessOutput = outputs.first()

        if not output:
            raise exceptions.ValidationError({"detail": "ProcessOutput mavjud emas."})

        material = output.material

        product, _ = Product.objects.select_for_update().get_or_create(
            organization=process.organization,
            material=material,
            defaults={
                "quantity": Q("0"),
                "purity": material.purity,
                "pure_gold": Q("0"),
            },
        )

        # umumiy miqdorni qo‘shish
        product.quantity = (product.quantity + Q(output.quantity)).quantize(Q("0.0001"))

        product.pure_gold = (product.pure_gold + total_pure_gold / (Q(material.purity) / Q("100"))).quantize(Q("0.0001"))

        product.save(update_fields=["quantity", "purity", "pure_gold"])

        # === 3) PROCESS ni yakunlash ===
        process.total_in = total_pure_gold.quantize(Q("0.0001"))
        process.total_out = total_pure_gold.quantize(Q("0.0001"))
        process.status = ProcessStatus.COMPLETED
        process.save(update_fields=["total_in", "total_out", "status"])

        return process
