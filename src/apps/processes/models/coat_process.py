from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from .base import BaseProcess


class CoatProcess(BaseProcess):
    """
    Temirli Oltin (Coat) Process
    Business Logic:
    - pure_gold = gold_input - scrap_output
    - iron_gold_output = gold_input + iron_input - scrap_output
    """

    gold_input = models.DecimalField(max_digits=15, decimal_places=4, help_text="Input pure gold mass")
    iron_input = models.DecimalField(max_digits=15, decimal_places=4, help_text="Input iron mass")

    scrap_output = models.DecimalField(max_digits=15, decimal_places=4, default=0, help_text="Output scrap mass", null=True, blank=True)
    iron_gold_output = models.DecimalField(max_digits=15, decimal_places=4, help_text="Output iron gold mass", null=True, blank=True)

    class Meta:
        verbose_name = "Coat Process"
        verbose_name_plural = "Coat Processes"

    def clean(self):
        if self.gold_input is not None and self.gold_input <= 0:
            raise ValidationError({"gold_input": "Gold input must be positive"})

        if self.iron_input is not None and self.iron_input <= 0:
            raise ValidationError({"iron_input": "Iron input must be positive"})

        if self.scrap_output is not None and self.scrap_output < 0:
            raise ValidationError({"scrap_output": "Scrap output cannot be negative"})

        # # Mass balance check if all fields are present
        # if all(x is not None for x in [self.gold_input, self.iron_input, self.scrap_output, self.iron_gold_output]):
        #     expected_output = self.gold_input + self.iron_input - self.scrap_output
        #     # Allow small floating point difference
        #     if abs(self.iron_gold_output - expected_output) > Decimal("0.001"):
        #         raise ValidationError(
        #             f"Mass mismatch: Expected iron_gold_output={expected_output}, got {self.iron_gold_output}"
        #         )

    @property
    def pure_gold(self):
        """Calculate pure gold content"""
        if self.gold_input is None or self.scrap_output is None:
            return Decimal("0")
        return self.gold_input - self.scrap_output

    def save(self, *args, **kwargs):
        self.full_clean()

        # Auto-calculate totals for BaseProcess
        if self.gold_input and self.iron_input:
            self.total_in = self.gold_input + self.iron_input

        if self.iron_gold_output and self.scrap_output is not None:
            self.total_out = self.iron_gold_output + self.scrap_output

        super().save(*args, **kwargs)
