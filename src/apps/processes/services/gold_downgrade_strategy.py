from decimal import Decimal as Q, ROUND_HALF_UP
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.processes.models import GoldDowngradeProcess
from apps.products.models import Product
from apps.common.choices.materials import MaterialType


class GoldDowngradeStrategy:
    """
    Gold Downgrade Strategy (999 -> 585)
    
    1. Take 999 Gold Product
    2. Add Alloy (Copper/Silver/etc - simplified as generic 'Alloy' or just mass increase)
    3. Result in 585 Gold Product
    """

    def __init__(self, process: GoldDowngradeProcess, data: dict):
        self.process = process
        self.data = data

    @transaction.atomic
    def execute(self):
        source_product: Product = self.data["source_product"]
        
        # 1. Consume Source (999)
        self._consume_source(source_product)
        
        # 2. Produce Target (585)
        self._produce_target()
        
        # 3. Finalize
        self.process.status = "completed"
        self.process.save()
        
        return self.process

    def _consume_source(self, product: Product):
        qty = self.process.gold_999_input
        
        if product.quantity < qty:
            raise ValidationError(f"Insufficient 999 gold: {product}")
            
        product.quantity = (product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        product.pure_gold = (product.pure_gold - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        product.save()

    def _produce_target(self):
        # Target is always Gold 585 for this process
        product, _ = Product.objects.get_or_create(
            organization=self.process.organization,
            material=MaterialType.GOLD_585,
            defaults={
                "quantity": 0,
                "purity": 585, # Fixed for 585
                "pure_gold": 0
            }
        )
        
        added_mass = self.process.gold_585_output
        pure_gold_content = self.process.pure_gold # Validated as = input 999
        
        product.quantity += added_mass
        product.pure_gold += pure_gold_content
        
        # Verify purity roughly matches 585
        # (pure / total) * 1000 ~= 585
        # We don't force it to strict 585 if mass balance says otherwise, 
        # but the Product model will store exact pure gold.
        
        product.save()
