from django.db import transaction

from apps.processes.models.process import ProcessStatus
from .base import BaseProcessStrategy


class AlloyStrategy(BaseProcessStrategy):
    """
    Alloy strategy
    Example 999 -> 585
    """

    @transaction.atomic
    def calculate(self):
        process = self.process

        self._validate_structure(process)

        # hisob-kitob keyin keladi
        self._calculate_and_apply(process)

        process.status = ProcessStatus.COMPLETED
        process.save(update_fields=["status"])

        return process
