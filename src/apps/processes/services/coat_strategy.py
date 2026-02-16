from decimal import Decimal as Q, ROUND_HALF_UP
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.processes.models import CoatProcess
from apps.products.models import Product
from apps.common.choices.materials import MaterialType


class CoatStrategyV2:
    """
    COAT (temirli oltin) Strategy for new CoatProcess model.
    Business Logic:
    - Input sources:
        - Gold Input (Product with pure gold)
        - Iron Input (Product or raw material)
    - Output targets:
        - Iron Gold Output (Composite Product)
        - Scrap Output (Product)
    
    The strategy:
    1. Validates inputs/outputs exist in request (handled by serializer/view usually, but here we process logic)
    2. Decrements source products
    3. Increments/Creates destination products
    4. Updates Process status
    """

    def __init__(self, process: CoatProcess, data: dict):
        self.process = process
        self.data = data
        self._validate_data()

    def _validate_data(self):
        # Data validation handled by serializer mostly, but we need specific fields
        required = ["gold_product", "iron_product"] 
        # Note: In the new design, we might pass product IDs or objects differently.
        # Assuming `data` contains cleaned_data from serializer with product instances or IDs.
        pass

    @transaction.atomic
    def execute(self):
        # 1. Extract inputs from data (passed from Serializer)
        gold_prod: Product = self.data["gold_product"]
        iron_prod: Product = self.data["iron_product"]
        
        gold_qty = self.process.gold_input
        iron_qty = self.process.iron_input
        
        # 2. Process Inputs (Decrement)
        self._process_input_product(gold_prod, gold_qty, is_gold_source=True)
        self._process_input_product(iron_prod, iron_qty, is_gold_source=False)
        
        # 3. Process Outputs (Increment)
        # 3.1 Iron Gold Output (Composite)
        self._process_composite_output()
        
        # 3.2 Scrap Output
        if self.process.scrap_output > 0:
            self._process_scrap_output()
            
        # 4. Finalize
        self.process.status = "completed"
        self.process.save()
        
        return self.process

    def _process_input_product(self, product: Product, qty: Q, is_gold_source: bool):
        if product.quantity < qty:
            raise ValidationError(f"Insufficient quantity for {product}")
            
        product.quantity = (product.quantity - qty).quantize(Q("0.0001"), rounding=ROUND_HALF_UP)
        
        if is_gold_source and product.pure_gold:
             # Calculate pure gold portion to remove
             # If using new model logic, pure gold input is exactly gold_input mass * purity (if 999) or just mass
             # But here we stick to business rule: pure_gold = gold_input - scrap_output 
             # So we just reduce product pure gold proportionally or strictly.
             # Strict approach:
             ratio = qty / (product.quantity + qty) # original quantity
             pg_remove = product.pure_gold * ratio
             product.pure_gold -= pg_remove
        
        product.save()

    def _process_composite_output(self):
        # Create or Update Iron Gold Product
        # Material: IRON_GOLD
        # Mass: process.iron_gold_output
        # Pure Gold: process.pure_gold (calculated property)
        
        product, _ = Product.objects.get_or_create(
            organization=self.process.organization,
            material=MaterialType.IRON_GOLD,
            is_composite=True,
            defaults={
                "quantity": 0,
                "purity": 0, 
                "pure_gold": 0
            }
        )
        
        product.quantity += self.process.iron_gold_output
        product.pure_gold += self.process.pure_gold
        
        # Recalculate purity
        if product.quantity > 0:
            product.purity = (product.pure_gold / product.quantity) * 100
            
        product.save()

    def _process_scrap_output(self):
        # Scrap Output (usually just mass, maybe some purity if it's gold scrap)
        # Requirement says: pure_gold = gold_input - scrap_output.
        # This implies scrap is IMPURE or LOSS? 
        # Or is scrap actually gold scrap?
        # "scrap_output >= 0". 
        # Business rule "pure_gold = gold_input - scrap_output" implies scrap contains NO pure gold recognized in the main output?
        # Actually usually scrap has gold. But the formula `pure_gold = gold_input - scrap_output` suggests 
        # that the pure gold content of the *resulting Coat* is what remains after scrap is removed.
        # So Scrap itself might be just waste or a separate byproduct.
        # Let's assume Scrap is MaterialType.SCRAP
        
        product, _ = Product.objects.get_or_create(
            organization=self.process.organization,
            material=MaterialType.SCRAP,
            defaults={
                "quantity": 0,
                "purity": 0,
                "pure_gold": 0
            }
        )
        
        product.quantity += self.process.scrap_output
        product.save()
