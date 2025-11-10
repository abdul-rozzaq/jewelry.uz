# ruff: noqa: F401


from django.db import transaction
from decimal import Decimal as Q, ROUND_HALF_UP
from rest_framework import exceptions

from apps.processes.models import ProcessInput, ProcessOutput, ProcessStatus

from .base import BaseProcessStrategy
from apps.products.models import Product


class DefaultStrategy(BaseProcessStrategy):
    """
    Bu ssenariyda hech qanday maxsus hisob-kitoblar amalga oshirilmaydi.
    Faqatgina kirish va chiqish ma'lumotlari tekshiriladi va saqlanadi.
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        inputs: list[ProcessInput] = process.inputs.select_related("product__material", "material").select_for_update()
        outputs: list[ProcessOutput] = process.outputs.select_related("material")

        total_input_qty = Q("0")  # sum((inp.quantity for inp in inputs), Q("0"))
        total_output_qty = Q("0")  # sum((out.quantity for out in outputs), Q("0"))

        # === 1) INPUTLAR: quantity ni kamaytirish ===
        for inp in inputs:
            product = inp.product
            material = inp.material or (product.material if product else None)

            qty = Q(inp.quantity)

            if qty <= Q("0"):
                raise exceptions.ValidationError({"detail": f"{material} miqdori musbat bo'lishi kerak."})

            if not material:
                raise exceptions.ValidationError({"detail": "ProcessInput uchun material topilmadi."})

            # product mavjud bo‘lsa, quantity ni kamaytirish
            if product:
                if product.quantity < qty:
                    raise exceptions.ValidationError({"detail": f"{product} mahsuloti yetarli emas."})

                product.quantity = (product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
                product.pure_gold = (product.pure_gold - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
                product.save(update_fields=["quantity", "pure_gold"])

                total_input_qty += qty * (product.purity / Q("100"))

        # === 2) OUTPUT: yangi mahsulotni yangilash yoki yaratish ===
        for output in outputs:
            material = output.material

            product, _ = Product.objects.select_for_update().get_or_create(
                organization=process.organization,
                material=material,
                defaults={
                    "quantity": Q("0"),
                    "purity": material.purity,
                },
            )

            product.quantity = (product.quantity + Q(output.quantity)).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
            product.pure_gold = (product.pure_gold + Q(output.quantity)).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)

            product.save(update_fields=["quantity", "pure_gold"])

            total_output_qty += Q(output.quantity) * (material.purity / Q("100"))

        process.total_in = total_input_qty.quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        process.total_out = total_output_qty.quantize(Q("0.0001"), rounding=ROUND_HALF_UP)

        process.status = ProcessStatus.COMPLETED

        process.save(update_fields=["total_in", "total_out", "status"])
