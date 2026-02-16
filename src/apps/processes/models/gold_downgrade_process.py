from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

from .base import BaseProcess


class GoldDowngradeProcess(BaseProcess):
    """
    Gold Downgrade Process (999 -> 585)
    Business Logic:
    - Input must be 999 purity
    - Output must be 585 purity (or target purity)
    - Pure gold mass must be preserved
    """
    gold_999_input = models.DecimalField(max_digits=15, decimal_places=4, help_text="Mass of 999 gold input")
    gold_585_output = models.DecimalField(max_digits=15, decimal_places=4, help_text="Mass of 585 gold output", null=True, blank=True)

    class Meta:
        verbose_name = "Gold Downgrade Process"
        verbose_name_plural = "Gold Downgrade Processes"

    def clean(self):
        if self.gold_999_input is not None and self.gold_999_input <= 0:
            raise ValidationError({"gold_999_input": "Input must be positive"})
            
        if self.gold_585_output is not None and self.gold_585_output <= 0:
            raise ValidationError({"gold_585_output": "Output must be positive"})
            
        # Basic mass check: Output mass should generally be higher than input mass (adding alloys)
        # for downgrading purity (e.g. 999 -> 585)
        if (self.gold_999_input and self.gold_585_output and 
            self.gold_585_output < self.gold_999_input):
             raise ValidationError("Output mass cannot be less than input mass for downgrade")

    @property
    def pure_gold(self):
        """For downgrade, pure gold is the input mass (approx, assuming 999 is ~100%)"""
        # In reality 999 is 99.9%, but for business logic often treated as pure base
        if self.gold_999_input is None:
            return Decimal("0")
        return self.gold_999_input

    def save(self, *args, **kwargs):
        self.full_clean()
        
        self.total_in = self.gold_999_input
        self.total_out = self.gold_585_output
            
        super().save(*args, **kwargs)
