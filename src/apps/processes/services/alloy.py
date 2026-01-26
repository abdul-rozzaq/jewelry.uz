from decimal import Decimal as Q
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.processes.services.base import BaseProcessStrategy
from apps.processes.models import ProcessStatus
from apps.products.models import Product
from apps.processes.models.process_template import ProcessItemRole


class AlloyStrategy(BaseProcessStrategy):
    """
    Gold purity lowering strategy.
    Example: 999 -> 585

    INPUT ROLES:
      - BASE_GOLD (gold 999)
      - METAL (copper / other metal)

    OUTPUT ROLES:
      - COMPOSITE (gold 585)

    Rules:
      - Pure gold is preserved
      - METAL only increases mass
      - Target purity is taken from output material.purity
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        template = self._get_template(process)
        input_roles, output_roles = self._get_role_maps(template)
        self._validate_structure(input_roles, output_roles)

        pure_gold, gold_mass, metal_mass = self._process_inputs(
            process, input_roles
        )
        output_material, target_purity = self._get_output_material(process)

        final_mass = self._calculate_final_mass(
            pure_gold, gold_mass, metal_mass, target_purity
        )

        self._update_output_product(
            process,
            output_material,
            final_mass,
            pure_gold,
            target_purity,
        )
        self._finalize_process(process, pure_gold)

        return process

    def _get_template(self, process):
        template = process.process_type.template
        if not template:
            raise ValidationError("ProcessType.template is required")
        return template

    def _get_role_maps(self, template):
        input_roles = {
            item.material_id: item.role
            for item in template.template_inputs.all()
        }
        output_roles = {
            item.material_id: item.role
            for item in template.template_outputs.all()
        }
        return input_roles, output_roles

    def _validate_structure(self, input_roles, output_roles):
        if ProcessItemRole.BASE_GOLD not in input_roles.values():
            raise ValidationError("BASE_GOLD input is required")

        if ProcessItemRole.METAL not in input_roles.values():
            raise ValidationError("METAL input is required")

        if list(output_roles.values()) != [ProcessItemRole.COMPOSITE]:
            raise ValidationError("Only COMPOSITE output is allowed")

    def _process_inputs(self, process, input_roles):
        inputs = (
            process.inputs
            .select_related("material", "product")
            .select_for_update()
        )

        pure_gold = Q("0")
        gold_mass = Q("0")
        metal_mass = Q("0")

        for inp in inputs:
            if not inp.material:
                raise ValidationError("Input material is required")

            role = input_roles.get(inp.material_id)
            if not role:
                raise ValidationError(
                    f"Material {inp.material} not allowed by template"
                )

            qty = Q(inp.quantity)

            if qty <= 0:
                raise ValidationError("Quantity must be positive")

            if role == ProcessItemRole.BASE_GOLD:
                gold_mass += qty
                pure_gold += qty * Q(inp.material.purity) / Q("100")
            elif role == ProcessItemRole.METAL:
                metal_mass += qty

            if inp.product:
                if inp.product.quantity < qty:
                    raise ValidationError(f"Not enough product: {inp.product}")

                inp.product.quantity -= qty
                inp.product.save(update_fields=["quantity"])

        return pure_gold, gold_mass, metal_mass

    def _get_output_material(self, process):
        output = process.outputs.select_related("material").first()
        if not output:
            raise ValidationError("Output is required")

        output_material = output.material
        target_purity = Q(output_material.purity)

        if target_purity <= 0:
            raise ValidationError("Output material purity must be set")

        return output_material, target_purity

    def _calculate_final_mass(
        self, pure_gold, gold_mass, metal_mass, target_purity
    ):
        final_mass = (pure_gold / target_purity) * Q("100")
        required_metal = final_mass - gold_mass

        if metal_mass < required_metal:
            raise ValidationError(
                f"Not enough metal. Required: {required_metal}, got: {metal_mass}"
            )

        return final_mass

    def _update_output_product(
        self, process, output_material, final_mass, pure_gold, target_purity
    ):
        product, _ = Product.objects.select_for_update().get_or_create(
            organization=process.organization,
            material=output_material,
            defaults={
                "quantity": Q("0"),
                "pure_gold": Q("0"),
                "purity": target_purity,
                "is_composite": True,
            },
        )

        product.quantity += final_mass
        product.pure_gold += pure_gold
        product.purity = target_purity
        product.save(
            update_fields=["quantity", "pure_gold", "purity", "is_composite"]
        )

    def _finalize_process(self, process, pure_gold):
        process.total_in = pure_gold
        process.total_out = pure_gold
        process.status = ProcessStatus.COMPLETED
        process.save(update_fields=["total_in", "total_out", "status"])
