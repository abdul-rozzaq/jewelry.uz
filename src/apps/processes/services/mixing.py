from django.db import transaction

from decimal import Decimal as Q


from .base import BaseProcessStrategy


from decimal import ROUND_HALF_UP
from rest_framework.exceptions import ValidationError

from apps.processes.models import ProcessStatus
from apps.products.models import Product
from apps.processes.models.process_template import ProcessItemRole

_DEC4 = Q("0.0001")
_DEC2 = Q("0.01")


class MixingStrategyV2(BaseProcessStrategy):
    """
    Temirli oltin + Qaynoq oltin -> Temirli oltin (pure_gold qo'shiladi)

    INPUT ROLES:
      - BASE_GOLD (temirli oltin input): pure_gold manbasi (product.pure_gold asosiy)
      - ADDITIVE_GOLD (qaynoq): pure_gold qo‘shadi

    OUTPUT ROLES:
      - COMPOSITE (yakuniy temirli oltin)
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        in_role_by_mat, out_role_by_mat = self._get_role_maps(process)
        self._validate_structure(process, in_role_by_mat, out_role_by_mat)

        totals = self._process_inputs(process, in_role_by_mat)  # {mass_in, pure_in}

        self._process_output(process, out_role_by_mat, totals)

        self._finalize_process(process, totals)

        return process

    # -------------------------
    # ROLE MAPS + VALIDATION
    # -------------------------

    def _get_role_maps(self, process):
        if not process.process_type or not process.process_type.template:
            raise ValidationError("ProcessType.template is required")

        template = process.process_type.template
        
        in_role_by_mat = {item.material_id: item.role for item in template.template_inputs.all()}
        out_role_by_mat = {item.material_id: item.role for item in template.template_outputs.all()}
        
        return in_role_by_mat, out_role_by_mat

    def _validate_structure(self, process, in_role_by_mat, out_role_by_mat):
        if not process.inputs.exists():
            raise ValidationError("Processda inputlar mavjud emas.")
        
        if not process.outputs.exists():
            raise ValidationError("Processda output mavjud emas.")

        in_roles = set(in_role_by_mat.values())
        
        if ProcessItemRole.BASE_GOLD not in in_roles:
            raise ValidationError("BASE_GOLD input required (temirli oltin)")
        
        if ProcessItemRole.ADDITIVE_GOLD not in in_roles:
            raise ValidationError("ADDITIVE_GOLD input required (qaynoq oltin)")

        out_roles = list(out_role_by_mat.values())
        
        if out_roles != [ProcessItemRole.COMPOSITE]:
            raise ValidationError("Only one COMPOSITE output is allowed")

    # -------------------------
    # INPUTS
    # -------------------------

    def _pure_removed_from_product(self, product: Product, qty: Q) -> Q:
        if not product or product.pure_gold is None:
            return Q("0")
        
        if not product.quantity or Q(product.quantity) <= 0:
            return Q("0")
        
        per_unit = Q(product.pure_gold) / Q(product.quantity)
        
        return per_unit * qty

    def _process_inputs(self, process, in_role_by_mat):
        inputs = process.inputs.select_related("material", "product").select_for_update()

        mass_in = Q("0")
        pure_in = Q("0")

        for inp in inputs:
            if inp.quantity is None or Q(inp.quantity) <= 0:
                raise ValidationError("Input quantity musbat bo‘lishi kerak.")
        
            if not inp.material:
                raise ValidationError("ProcessInput.material required (hozircha).")

            role = in_role_by_mat.get(inp.material_id)
        
            if not role:
                raise ValidationError(f"Input material {inp.material} template'da ruxsat etilmagan.")

            qty = Q(inp.quantity)
            mass_in += qty

            # pure_gold accumulation
            if role in (ProcessItemRole.BASE_GOLD, ProcessItemRole.ADDITIVE_GOLD):
                if inp.product:
                    pg = self._pure_removed_from_product(inp.product, qty)
        
                    if pg == 0:
                        pg = qty * Q(inp.material.purity) / Q("100")
        
                    pure_in += pg
                else:
                    pure_in += qty * Q(inp.material.purity) / Q("100")
            else:
                raise ValidationError(f"Bu strategiyada ruxsat etilmagan input role: {role}")

            # decrease stock
            if inp.product:
                prod = inp.product
                if Q(prod.quantity) < qty:
                    raise ValidationError(f"{prod} mahsuloti yetarli emas.")

                prod.quantity = (Q(prod.quantity) - qty).quantize(_DEC4, rounding=ROUND_HALF_UP)

                if prod.pure_gold is not None:
                    pg = self._pure_removed_from_product(prod, qty)
                    if pg == 0:
                        pg = qty * Q(inp.material.purity) / Q("100")
                    prod.pure_gold = (Q(prod.pure_gold) - pg).quantize(_DEC4, rounding=ROUND_HALF_UP)

                prod.save(update_fields=["quantity", "pure_gold"])

        return {"mass_in": mass_in, "pure_in": pure_in}

    # -------------------------
    # OUTPUT
    # -------------------------

    def _process_output(self, process, out_role_by_mat, totals):
        out = process.outputs.select_related("material").first()
        
        if not out:
            raise ValidationError("Output required")

        role = out_role_by_mat.get(out.material_id)
        
        if role != ProcessItemRole.COMPOSITE:
            raise ValidationError("Output must be COMPOSITE material from template")

        out_qty = Q(out.quantity) if out.quantity and Q(out.quantity) > 0 else totals["mass_in"]

        out_mat = out.material
        
        out_prod, _ = Product.objects.select_for_update().get_or_create(
            organization=process.organization,
            material=out_mat,
            defaults={"quantity": Q("0"), "pure_gold": Q("0"), "purity": out_mat.purity, "is_composite": True},
        )

        out_prod.quantity = (Q(out_prod.quantity) + out_qty).quantize(_DEC4, rounding=ROUND_HALF_UP)
        out_prod.pure_gold = (Q(out_prod.pure_gold) + totals["pure_in"]).quantize(_DEC4, rounding=ROUND_HALF_UP)

        if out_prod.quantity > 0:
            out_prod.purity = ((out_prod.pure_gold / out_prod.quantity) * Q("100")).quantize(_DEC2, rounding=ROUND_HALF_UP)

        out_prod.save(update_fields=["quantity", "pure_gold", "purity", "is_composite"])

    # -------------------------
    # FINALIZE
    # -------------------------
 
    def _finalize_process(self, process, totals):
        process.total_in = totals["pure_in"].quantize(_DEC4, rounding=ROUND_HALF_UP)
        process.total_out = totals["pure_in"].quantize(_DEC4, rounding=ROUND_HALF_UP)
        process.status = ProcessStatus.COMPLETED
        process.save(update_fields=["total_in", "total_out", "status"])
