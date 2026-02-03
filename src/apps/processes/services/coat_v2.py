from decimal import ROUND_HALF_UP, Decimal as Q
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.processes.services.base import BaseProcessStrategy
from apps.processes.models.process_template import ProcessItemRole
from apps.processes.models import ProcessStatus
from apps.products.models import Product


class CoatStrategyV2(BaseProcessStrategy):
    """
    COAT (temirli oltin) - simplified role-based strategy.

    Rules:
      - Decrease input product quantities
      - Calculate pure gold from inputs (BASE_GOLD role only)
      - Distribute pure gold: composite gets (input - scrap)
      - Increase output product quantities
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        # Template va role maps olish
        in_role_by_mat, out_role_by_mat = self._get_role_maps(process)

        # Input mahsulotlardan kamaytirish va pure gold hisoblash
        total_pure_gold_in = self._process_inputs(process, in_role_by_mat)

        # Output mahsulotlarni yaratish/yangilash
        self._process_outputs(process, out_role_by_mat, total_pure_gold_in)

        # Processni tugatish
        self._finalize_process(process, total_pure_gold_in, out_role_by_mat)

        return process

    def _get_role_maps(self, process):
        """Template dan role mapping olish"""
        if not process.process_type or not process.process_type.template:
            raise ValidationError("ProcessType.template is required for COAT")

        template = process.process_type.template

        in_role_by_mat = {item.material_id: item.role for item in template.template_inputs.all()}
        out_role_by_mat = {item.material_id: item.role for item in template.template_outputs.all()}

        return in_role_by_mat, out_role_by_mat

    def _process_inputs(self, process, in_role_by_mat):
        """Input product'lardan quantity kamaytirish va pure gold hisoblash"""
        inputs = process.inputs.select_related("material", "product").select_for_update()

        if not inputs.exists():
            raise ValidationError("Processda inputlar mavjud emas.")

        total_pure_gold_in = Q("0")

        for inp in inputs:
            if inp.quantity is None or Q(inp.quantity) <= 0:
                raise ValidationError("Input quantity musbat bo'lishi kerak.")

            material = inp.material or (inp.product.material if inp.product else None)

            if not material:
                raise ValidationError("ProcessInput.material required.")

            role = in_role_by_mat.get(material.id)

            if not role:
                raise ValidationError(f"Input material {material} template'da ruxsat etilmagan.")

            qty = Q(inp.quantity)

            # Pure gold faqat BASE_GOLD dan
            if role == ProcessItemRole.BASE_GOLD:
                total_pure_gold_in += qty * Q(material.purity) / Q("100")
            elif role == ProcessItemRole.METAL:
                pass  # Temir faqat massa, pure gold yo'q
            else:
                raise ValidationError(f"COAT uchun input role noto'g'ri: {role}")

            # Product quantity kamaytirish
            if inp.product:
                if inp.product.quantity < qty:
                    raise ValidationError(f"{inp.product} mahsuloti yetarli emas.")

                inp.product.quantity = (inp.product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
                inp.product.save(update_fields=["quantity"])

        return total_pure_gold_in

    def _process_outputs(self, process, out_role_by_mat, total_pure_gold_in):
        """Output product'larni yaratish yoki yangilash"""
        outputs = process.outputs.select_related("material").all()

        if not outputs.exists():
            raise ValidationError("Processda outputlar mavjud emas.")

        # Output'larni composite va scrap ga ajratish
        composite_out = None
        scrap_outs = []

        for out in outputs:
            if out.quantity is None or Q(out.quantity) <= 0:
                raise ValidationError("Output quantity musbat bo'lishi kerak.")

            role = out_role_by_mat.get(out.material_id)
            if not role:
                raise ValidationError(f"Output material {out.material} template'da ruxsat etilmagan.")

            if role == ProcessItemRole.COMPOSITE:
                if composite_out is not None:
                    raise ValidationError("COAT uchun faqat bitta COMPOSITE output bo'lishi kerak.")
                composite_out = out
            elif role == ProcessItemRole.SCRAP:
                scrap_outs.append(out)
            else:
                raise ValidationError(f"COAT uchun output role noto'g'ri: {role}")

        if composite_out is None:
            raise ValidationError("COAT uchun COMPOSITE output shart.")

        # Scrap pure gold hisoblash
        scrap_pure_gold = Q("0")
        for s in scrap_outs:
            qty = Q(s.quantity)
            scrap_pure_gold += qty * Q(s.material.purity) / Q("100")

        if scrap_pure_gold > total_pure_gold_in:
            raise ValidationError("Hurda pure gold input pure golddan katta bo'lishi mumkin emas.")

        composite_pure_gold = (total_pure_gold_in - scrap_pure_gold).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)

        # Composite product yaratish/yangilash
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
        comp_prod.save(update_fields=["quantity", "pure_gold", "purity", "is_composite"])

        # Scrap product'larni yaratish/yangilash
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

    def _finalize_process(self, process, total_pure_gold_in, out_role_by_mat):
        """Process statusini completed ga o'zgartirish"""
        # Scrap pure gold qayta hisoblash
        outputs = process.outputs.select_related("material").all()
        scrap_pure_gold = Q("0")

        for out in outputs:
            role = out_role_by_mat.get(out.material_id)
            if role == ProcessItemRole.SCRAP:
                qty = Q(out.quantity)
                scrap_pure_gold += qty * Q(out.material.purity) / Q("100")

        process.total_in = total_pure_gold_in.quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        process.total_out = (total_pure_gold_in - scrap_pure_gold).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        process.status = ProcessStatus.COMPLETED
        process.save(update_fields=["total_in", "total_out", "status"])
