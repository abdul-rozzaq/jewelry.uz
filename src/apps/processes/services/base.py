from rest_framework import exceptions

from apps.processes.models import Process


class BaseProcessStrategy:
    """
    IMPORTANT ARCHITECTURE RULE:

    - Business logic is ROLE-BASED.
    - Never infer behavior from Material fields.
    - Always use ProcessTemplateItem.role for calculations.
    - Strategies must be deterministic based on roles.

    This rule is non-negotiable.
    """

    def __init__(self, process: Process):
        self.process = process

    def validate_inputs(self):
        if not self.process.inputs.exists():
            raise exceptions.ValidationError({"detail": "Processda inputlar mavjud emas."})

    def calculate(self):
        """Har bir subclass o‘zining hisoblash metodini yozadi"""
        raise NotImplementedError("Har bir strategiyada calculate() yozilishi kerak.")
