from django.db import transaction

from decimal import Decimal as Q


from apps.processes.models import Process, ProcessInput, ProcessOutput
from .base import BaseProcessStrategy


class MixingStrategy(BaseProcessStrategy):
    """
    Bu class TemirliOltin va QaynoqOltinni bir biriga qo'shish jarayonini bajaradi.
    """

    @transaction.atomic
    def calculate(self):
        process: Process = self.process

        inputs: list[ProcessInput] = process.inputs.select_related("product__material", "material").select_for_update()
        outputs: list[ProcessOutput] = process.outputs.select_related("material")

        total_pure_gold = Q("0")
        
        
        