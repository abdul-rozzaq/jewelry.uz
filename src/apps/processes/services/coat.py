from rest_framework import exceptions
from decimal import ROUND_HALF_UP, Decimal as Q
from django.db import transaction, models


from rest_framework.exceptions import ValidationError

from apps.processes.services.base import BaseProcessStrategy
from apps.processes.models.process_template import ProcessItemRole
from apps.materials.models import Material
from apps.processes.models import ProcessStatus
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


class CoatStrategyV2(BaseProcessStrategy):
    """
    COAT (temirli oltin) - minimal role-based algorithm.

    Input:
      - BASE_GOLD (e.g. gold 585): contributes to pure_gold + mass
      - METAL (iron): contributes only to mass

    Output:
      - COMPOSITE (temirli oltin): quantity comes from ProcessOutput.quantity
      - SCRAP (hurda): quantity comes from ProcessOutput.quantity

    Rule:
      composite_pure_gold = input_pure_gold - scrap_pure_gold
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        if not process.process_type or not process.process_type.template:
            raise ValidationError("ProcessType.template is required for COAT")

        template = process.process_type.template

        # --- role maps: material_id -> role (from template)
        in_role_by_mat = {item.material_id: item.role for item in template.template_inputs.all()}
        out_role_by_mat = {item.material_id: item.role for item in template.template_outputs.all()}

        # --- fetch inputs/outputs
        inputs = process.inputs.select_related("material", "product").select_for_update()
        outputs = process.outputs.select_related("material")

        if not inputs.exists():
            raise ValidationError("Processda inputlar mavjud emas.")
        if not outputs.exists():
            raise ValidationError("Processda outputlar mavjud emas.")

        # --- compute input pure gold and total mass
        total_pure_gold_in = Q("0")
        total_mass_in = Q("0")

        for inp in inputs:
            if inp.quantity is None or Q(inp.quantity) <= 0:
                raise ValidationError("Input quantity musbat bo'lishi kerak.")

            if not inp.material:
                raise ValidationError("ProcessInput.material required (for now).")

            role = in_role_by_mat.get(inp.material_id)
            if not role:
                raise ValidationError(f"Input material {inp.material} template'da ruxsat etilmagan.")

            qty = Q(inp.quantity)

            if role == ProcessItemRole.BASE_GOLD:
                total_pure_gold_in += qty * Q(inp.material.purity) / Q("100")
                total_mass_in += qty
            elif role == ProcessItemRole.METAL:
                total_mass_in += qty
            else:
                raise ValidationError(f"COAT uchun input role noto‘g‘ri: {role}")

            # decrease stock if product provided
            if inp.product:
                if inp.product.quantity < qty:
                    raise ValidationError(f"{inp.product} mahsuloti yetarli emas.")
                inp.product.quantity = (inp.product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
                inp.product.save(update_fields=["quantity"])

        # --- classify outputs (by material role)
        composite_out = None
        scrap_outs = []

        total_mass_out = Q("0")

        for out in outputs:
            if out.quantity is None or Q(out.quantity) <= 0:
                raise ValidationError("Output quantity musbat bo'lishi kerak.")

            role = out_role_by_mat.get(out.material_id)
            if not role:
                raise ValidationError(f"Output material {out.material} template'da ruxsat etilmagan.")

            qty = Q(out.quantity)
            total_mass_out += qty

            if role == ProcessItemRole.COMPOSITE:
                if composite_out is not None:
                    raise ValidationError("COAT uchun faqat bitta COMPOSITE output bo‘lishi kerak.")
                composite_out = out
            elif role == ProcessItemRole.SCRAP:
                scrap_outs.append(out)
            else:
                raise ValidationError(f"COAT uchun output role noto‘g‘ri: {role}")

        if composite_out is None:
            raise ValidationError("COAT uchun COMPOSITE output shart.")

        # --- simple mass-balance validation (minimal)
        if total_mass_out > total_mass_in:
            raise ValidationError("Output mass input massdan katta bo‘lishi mumkin emas.")

        # --- compute scrap pure gold (can be 0 if scrap purity 0)
        scrap_mass = Q("0")
        scrap_pure_gold = Q("0")

        for s in scrap_outs:
            qty = Q(s.quantity)
            scrap_mass += qty
            scrap_pure_gold += qty * Q(s.material.purity) / Q("100")

        if scrap_pure_gold > total_pure_gold_in:
            raise ValidationError("Hurda pure gold input pure golddan katta bo‘lishi mumkin emas.")

        composite_pure_gold = (total_pure_gold_in - scrap_pure_gold).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)

        # --- update/create output products
        # 1) COMPOSITE product
        composite_material = composite_out.material
        comp_prod, _ = Product.objects.select_for_update().get_or_create(
            organization=process.organization,
            material=composite_material,
            defaults={
                "quantity": Q("0"),
                "purity": composite_material.purity,
                "pure_gold": Q("0"),
                "is_composite": True,
            },
        )

        comp_qty = Q(composite_out.quantity)
        comp_prod.quantity = (comp_prod.quantity + comp_qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        comp_prod.pure_gold = (comp_prod.pure_gold + composite_pure_gold).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        # purityni hozir hisoblamaymiz (soddalashtirish), material.purity qolsin
        comp_prod.save(update_fields=["quantity", "pure_gold", "purity", "is_composite"])

        # 2) SCRAP product(s) (ixtiyoriy, lekin to‘g‘ri audit uchun saqlaymiz)
        for s in scrap_outs:
            scrap_material = s.material
            sp, _ = Product.objects.select_for_update().get_or_create(
                organization=process.organization,
                material=scrap_material,
                defaults={
                    "quantity": Q("0"),
                    "purity": scrap_material.purity,
                    "pure_gold": Q("0"),
                    "is_composite": False,
                },
            )
            qty = Q(s.quantity)
            pg = qty * Q(scrap_material.purity) / Q("100")

            sp.quantity = (sp.quantity + qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
            sp.pure_gold = (sp.pure_gold + pg).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
            sp.save(update_fields=["quantity", "pure_gold", "purity", "is_composite"])

        # --- finalize process
        process.total_in = total_pure_gold_in.quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        process.total_out = (total_pure_gold_in - scrap_pure_gold).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        process.status = ProcessStatus.COMPLETED
        process.save(update_fields=["total_in", "total_out", "status"])

        return process
